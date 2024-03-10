import socket
import loguru
from threading import Lock
# init 
loguru.logger.add("error.log", format="{time} {level} {message}", level="ERROR", rotation="1 MB", compression="zip")

class Sock_Ser():
    def __init__(self,ip,port):
        self._ip = ip
        self._port = port
        self._threads_lock = Lock()
        self._list_lock = Lock()
        self._client_list = [] # (conn,addr)

    def bind(self):
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._sock.bind((self._ip,self._port))
        self._sock.listen(5)

    def accept(self):
        '''
        if new client connect, return conn and addr
        if the client already in the list, return None
        '''
        conn,addr = self._sock.accept()
        if conn not in self._client_list:
            if self._list_lock.acquire():
                self._client_list.append((conn,addr))
                self._list_lock.release()
        else:
            conn = None
            addr = None
        return conn,addr
    
    def get_client_num(self):
        if self._list_lock.acquire():
            num = len(self._client_list)
            self._list_lock.release()
        return num

    def get_client_info(self):
        if self._list_lock.acquire():
            client_list = [i[1] for i in self._client_list]
            print(client_list)
            self._list_lock.release()
        return client_list
    
    def send_msg(self,conn,msg):
        conn.send(msg.encode("utf-8"))

    def get_client_socket(self,addr:tuple)->socket.socket:
        '''
        use addr to get the client's socket
        param: 
            addr tuple
        '''
        if self._list_lock.acquire():
            for i in self._client_list:
                if addr == i[1]:
                    return i[0]
            self._list_lock.release()
       
    
    



