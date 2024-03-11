import socket
import loguru
from threading import Lock
import select

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
        try:
            conn,addr = self._sock.accept()
            if conn not in self._client_list:
                if self._list_lock.acquire():
                    self._client_list.append((conn,addr))
                    self._list_lock.release()
            else:
                conn = None
                addr = None
        except socket.timeout:
            pass
        return conn,addr
    
    def get_client_num(self):
        if self._list_lock.acquire():
            num = len(self._client_list)
            self._list_lock.release()
        return num

    def get_client_info(self):
        if self._list_lock.acquire():
            client_list = [i[1] for i in self._client_list]
            self._list_lock.release()
        return client_list
    
    def send_msg(self,conn:socket.socket,msg):
        try:
            conn.send(msg.encode("utf-8"))
            return True
        except Exception as e:
            loguru.logger.error(e)
            return False

    def recv_msg(self,conn:socket.socket,time=None):
        '''
        recv msg from the conn, if time is None, then block
        '''
        if time is None:
            conn.recv(1024)
        else:
            inputs = [conn]
            outputs = []
            while True:
                readable,writeable,exceptional = select.select(inputs,outputs,inputs,time)
                if not (readable or writeable or exceptional):
                    raise TimeoutError
                for s in readable:
                    if s is conn:
                        data = conn.recv(1024)
                        return data.decode("utf-8")
                    else:
                        raise Exception("error")
                    
    def get_client_socket(self,addr:tuple)->socket.socket:
        '''
        use addr to get the client's socket
        param: 
            addr tuple
        ''' 

        if self._list_lock.acquire():
            for i in self._client_list:
                if i[1] == addr:
                    self._list_lock.release()
                    return i[0]
            self._list_lock.release()
        return None
       
    
    



