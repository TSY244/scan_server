import socket
import os
import struct
import pickle

server_ip = '127.0.0.1'
server_port = 5400
# filepath = os.path.dirname(os.path.abspath(__file__))

def get(filepath,file_name, client):
    file_path = os.path.join(filepath, file_name)
    if os.path.isfile(file_path):
        header = {
            'file_name': "config.ini",
            'file_size': os.path.getsize(file_path)
        }
        header_bytes = pickle.dumps(header)
        client.send(struct.pack('i', len(header_bytes)))
        client.send(header_bytes)
        with open(file_path, 'rb') as f:
            for line in f:
                client.send(line)
    else:
        client.send(struct.pack('i', 0))


def run(server,client,file_path,file_name):
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.bind((server_ip, server_port))
    # server.listen(5)
    print('Server start on')
    print('-> ip: %s port: %d' %(server_ip, server_port))
    # while True:
    #     client, addr = server.accept()
    print('A new connection from %s' % client)
    try:
        get(file_path,file_name, client)
    except ConnectionResetError:
        print("ConnectionResetError")




# def run():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((server_ip, server_port))
#     server.listen(5)
#     print('Server start on')
#     print('-> ip: %s port: %d' %(server_ip, server_port))
#     while True:
#         client, addr = server.accept()
#         print('A new connection from %s' % addr[0])
#         while True:
#             try:
#                 request = client.recv(1024).decode('utf-8')
#                 print('Send %s to %s' % (request, addr[0]))
#                 get(request, client)
#             except ConnectionResetError:
#                 break
#         client.close()
#     server.close()

if __name__ == '__main__':
    run()