import socket
import loguru
import configparser
import sys
import os
import tools.ip.ip_tools as ip_tools 
import tools.socket.server as socket_server
import tools.socket.client as socket_client
from  threading import Thread,Lock,Event
import configparser



# get if debug
config=configparser.ConfigParser()
config.read("config.ini")
g_debug=config["COMMON"]["debug"]

# init loguru
loguru.logger.add("log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

class Wroker(): 
    RED="\033[0;31;40m"
    GREEN="\033[0;32;40m"
    BLUE="\033[0;34;40m"
    END="\033[0m"
    def __init__(self,ip,port):
        '''
        param:
            ip: server ip
            port: server port
        '''
        super().__init__()
        try:
            if not ip_tools.check_ip_if_valid(ip):
                raise ValueError("ip is not valid")
            if not 0<=port<=65535:
                raise ValueError("port is not valid")
        except Exception as e:
            loguru.logger.error(e)
            sys.exit(1)
        
        self._client_threads=[]
        self._threads_lock=Lock()
        
        self.socket_server=socket_server.Sock_Ser(ip,port)
        self.socket_server.bind()


        # run server to send message
        run_server_t = Thread(target=self._run_server)
        run_server_t.start()
        # self._run_server()        

    def _run_server(self):
        while True:
            conn,addr = self.socket_server.accept()
            if g_debug:
                loguru.logger.info(f"connect from {addr}")
            else:
                print(self.GREEN+"[+] <client_info> connect from "+str(addr)+self.END)
                
    def send_cmd(self,cmd:str,addr:str):
        '''
        send command to client
        param:
            cmd: command
            addr: client ip:port
        return:
            bool: if send success
        '''
        ip=addr.split(":")[0]
        port=int(addr.split(":")[1])

        if not ip_tools.check_ip_if_valid(ip):
            print(self.RED+"[-] ip is not valid"+self.END)
            return False,None
        if not 0<=port<=65535:
            print(self.RED+"[-] port is not valid"+self.END)
            return False,None
        
        conn=self.socket_server.get_client_socket((ip,port))
        try:
            if not self.socket_server.send_msg(conn,cmd):
                print(self.RED+"[-] send cmd failed"+self.END)
            ret= self.socket_server.recv_msg(conn,5)
            return True,ret
        except TimeoutError:
            return True,None
        except Exception as e:
            loguru.logger.error(e)
            return False,None

        

    def get_client(self)->list:
        return self.socket_server.get_client_info()
    
    def get_client_num(self):
        return self.socket_server.get_client_num()


