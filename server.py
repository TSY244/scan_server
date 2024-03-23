"""
use redis as message queue
this can scan ip range and add ip to redis
"""

import sys
import configparser
import loguru
import time
import signal
import os
import tools.redis.my_redis as my_redis
import tools.ip.ip_tools as ip_tools
import tools.socket.client as client_tools
import tools.socket.server as server_tools
from threading  import Thread
# init loguru
loguru.logger.add("/log/error.log", rotation="500 MB", retention="10 days", level="ERROR")


# get debug
config=configparser.ConfigParser()
config.read("config.ini")
g_debug=int(config["COMMON"]["debug"])


# 添加信号
def signal_handler(signal, frame):
    loguru.logger.error("{0}  -->  {1}".format(signal, frame))
    pid = os.getpid()
    os.kill(pid, signal)


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    ips = config['IP_RANGE']['ip']

    redis_host = config['REDIS']['redis_host']
    redis_port = config['REDIS']['redis_port']
    redis_password = config['REDIS']['redis_password']
    message_name = config['REDIS']['message_queue']

    return ips, redis_host, redis_port, redis_password, message_name

def check_redis(redis_host, redis_port, redis_password):
    # each 5 seconds, try to connect redis, and connect 100 times 
    now_times = 0
    max_times = 100

    ip_tools.check_ip_if_valid(redis_host)

    try:
        while now_times < max_times:
            if my_redis.Redis.check_if_connectable(redis_host, redis_port, redis_password):
                return
            loguru.logger.info("can't connect redis")
            now_times += 1
            time.sleep(5)
        raise Exception
    except:
        loguru.logger.error("redis connect error")
        sys.exit(1)

def add_ip_to_redis(ip_start, ip_end, redis_cli: my_redis.Redis):
    # get ip from ip_start to ip_end
    a_ip_start, b_ip_start, c_ip_start, d_ip_start = ip_start.split('.')
    a_ip_end, b_ip_end, c_ip_end, d_ip_end = ip_end.split('.')
    a_ip_start, b_ip_start, c_ip_start, d_ip_start = int(a_ip_start), int(b_ip_start), int(c_ip_start), int(d_ip_start)
    a_ip_end, b_ip_end, c_ip_end, d_ip_end = int(a_ip_end), int(b_ip_end), int(c_ip_end), int(d_ip_end) + 1

    # index
    index = 0
    while True:
        ip = "{}.{}.{}.{}".format(a_ip_start, b_ip_start, c_ip_start, d_ip_start)
        if g_debug == 1:
            if not d_ip_start > 255:
                loguru.logger.info("test ip: {}".format(ip))

        if a_ip_start == a_ip_end and b_ip_start == b_ip_end and c_ip_start == c_ip_end and d_ip_start == d_ip_end:
            break

        # add ip to redis
        # if redis_cli.add_message(f"key_{index}", ip) == False:
        #     loguru.logger.error("add ip to redis failed")

        if g_debug == 1:
            with open('ip.txt', 'a') as f:
                f.write(ip + '\n')
        if redis_cli.add_message(ip) == False:
            loguru.logger.error("add ip to redis failed")

        # get ip between ip_start and ip_end
        if d_ip_start > 255:
            d_ip_start = 0
            c_ip_start += 1
        if c_ip_start >= 255:
            c_ip_start = 0
            b_ip_start += 1
        if b_ip_start >= 255:
            b_ip_start = 0
            a_ip_start += 1
        index += 1
        d_ip_start += 1

def server_main():
    server=server_tools.Sock_Ser("127.0.0.1", 9999)
    server.bind()
    while True:
        conn,addr = server.accept()
        client = client_tools.Sock_Cli(conn,addr)
        loguru.logger.info("client num: {}".format(server.get_client_num()))

def main():
    # get config
    ips, redis_host, redis_port, redis_password, message_queue_name = get_config()
    if redis_password == 'None':
        redis_password = None

    # check redis host and port
    check_redis(redis_host, redis_port, redis_password)

    # get ip start and end
    ip_start, ip_end = ip_tools.get_ip_start_and_ipend(ips)
    loguru.logger.info("ip_start: {}, ip_end: {}".format(ip_start, ip_end))

    # connect to redis
    redis_cli = my_redis.Redis(redis_host=redis_host, redis_port=redis_port,
                               redis_password=redis_password,
                               message_name=message_queue_name)
    redis_cli.connect()

    # start socket server
    server_thread = Thread(target=server_main)
    server_thread.start()


    # can not connect
    can_not_connect_ip = []
    keys = []
    while True:
        # add ip to redis
        add_ip_to_redis(ip_start, ip_end, redis_cli)

        if g_debug == 1:
            time.sleep(360)
            # get all ack keys
            keys = my_redis.Redis.get_all_keys(redis_cli.redis_cli)

        if  len(keys)==1: # keys only have message_queue_name
            time.sleep(300)
            continue
        
        for key in keys:
            if key == message_queue_name:
                continue
            if key in can_not_connect_ip:
                redis_cli.delete_ack_value(key)
                can_not_connect_ip.remove(key)
            else:
                value = redis_cli.get_ack_value()
                can_not_connect_ip.append((key, value))

        

        time.sleep(60)

if __name__ == "__main__":
    # add signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
