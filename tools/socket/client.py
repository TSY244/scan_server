import socket


class Sock_Cli():
    '''
    client action
    '''
    def __init__(self,conn:socket.socket,addr):
        self._conn = conn
        self._addr = addr

    