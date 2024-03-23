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
import tools.UseElasticSearch.UseElasticSearch as es
import signal
import time
import tools.FileTransfer.server_tcp as upload_server

# get if debug
config=configparser.ConfigParser()
config.read("config.ini")
g_debug=int(config["COMMON"]["debug"])

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

        self._clent_status={}
        
        # self._client_threads=[]
        # self._threads_lock=Lock()
        
        self.socket_server=socket_server.Sock_Ser(ip,port)
        self.socket_server.bind()

        # run server to send message
        run_server_t = Thread(target=self._run_server)
        run_server_t.start()

        # run check socket
        check_socket_t = Thread(target=self._run_check_socket)
        check_socket_t.start()
        
        # self._run_server()

        # es
        es_config=Wroker._get_config()
        es_host=es_config["host"]
        es_port=es_config["port"]
        self._es_info_index=es_config["info_index"]
        self._es_vuls_index=es_config["vuls_index"]
        if not ip_tools.check_ip_if_connectable(es_host):
            loguru.logger.error("es host is not connectable")
            pid=os.getpid()
            os.kill(pid,signal.SIGTERM)
        self._es=es.MyElasticSearch(es_host,es_port)
        self._es.connect()

        # remote load config
        

    def _check_socket(self):
        '''
        check if socket is connectable
        '''
        clients=self.socket_server.get_client()
        for client in clients:
            if not self.socket_server.check_socket(client[0]):
                self.socket_server.delete_client(client[1])

    def _run_check_socket(self):
        while True:
            self._check_socket()
            time.sleep(60) 
             
    def _get_config():
        config=configparser.ConfigParser()
        config.read("config.ini")

        # es
        es_host=config["elasticsearch"]["host"]
        es_port=int(config["elasticsearch"]["port"])
        es_info_index=config["elasticsearch"]["info_index"]
        es_vuls_index=config["elasticsearch"]["vuls_index"]
        es={
            "host":es_host,
            "port":es_port,
            "info_index":es_info_index,
            "vuls_index":es_vuls_index
        }

        return es

    def _get_file_path(self):
        file_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if g_debug:
            loguru.logger.info(file_path)
        return file_path
            
    
    def _run_server(self):
        while True:
            conn,addr = self.socket_server.accept()
            # file_path=self._get_file_path()
            # if g_debug:
            #     loguru.logger.info(file_path)
            # upload_server.run(self.socket_server,conn,file_path,"config.ini")
            self.set_client_status(addr,"running")
            if g_debug:
                loguru.logger.info(f"connect from {addr}")
            else:
                print(self.GREEN+"[+] <client_info> connect from "+str(addr)+self.END)
                
    def send_cmd(self,cmd:str,addr:str,*args):
        '''
        send command to client
        param:
            cmd: command
            addr: client ip:port
            args: command's args
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
            if cmd=="kill":
                self.socket_server.close_client(conn)
                return True,None
            ret= self.socket_server.recv_msg(conn,5)
            return True,ret
        except TimeoutError:
            return True,None
        except Exception as e:
            loguru.logger.error(e)
            return False,None

    def get_client_status(self,addr:tuple):
        return self._clent_status[addr]

    def set_client_status(self,addr:tuple,status:str):
        self._clent_status[addr]=status

    def get_client(self)->list:
        return self.socket_server.get_client_info()
    
    def get_client_num(self):
        return self.socket_server.get_client_num()
    
    def get_es_info_num(self):
        return self._es.get_index_num(self._es_info_index)
    
    def get_es_vuls_num(self):
        return self._es.get_index_num(self._es_vuls_index)
    
    def delete_es_index(self,index:str):
        try:
            ret=self._es.delete_index(index)
        except Exception as e:
            return False
    
        
