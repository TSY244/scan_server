import socket
import select
import time

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("0.0.0.0",9999))
server.listen(5)
print("server start")
conn,addr=server.accept()
print(f"connect from {addr}")

inputs=[]
inputs.append(conn)
outputs=[]
timeout=10

while True:
    readable,writeable,exceptional=select.select(inputs,outputs,inputs,timeout)
    if not (readable or writeable or exceptional):
        print("Time out")
        break
    for s in readable:
        if s is conn:
            data=conn.recv(1024)
            print(f"recv data:{data}")
            conn.send(data)
        else:
            print("error")
            break


# import tools.cmd_tools.cmd_tools as cmd_tools

# # print("\033[0;31;40m我是小杨我就这样\033[0m")
# # print("\033[0;32;40m我是小杨我就这样\033[0m")
# # print("\033[0;33;40m我是小杨我就这样\033[0m")
# # print("\033[0;34;40m我是小杨我就这样\033[0m")
# # print("\033[0;35;40m我是小杨我就这样\033[0m")
# # print("\033[0;36;40m我是小杨我就这样\033[0m")
# # print("\033[0;37;40m我是小杨我就这样\033[0m")


# app=cmd_tools.APP("0.0.0.0", 9999)
# app.cmdloop()

