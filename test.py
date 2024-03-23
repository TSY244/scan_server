import socket
import tools.FileTransfer.server_tcp as upload_file
import os
import configparser




server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("127.0.0.1",9999))
server.listen(5)

client,addr=server.accept()

config=configparser.ConfigParser()
config.read("config.ini")
file_path=config["COMMON"]["cli_conf_path"]

upload_file.run(server,client,file_path,"client_config.ini")


# print(use_es.get_index_num())
