import cmd
import cmd_tools.woker as woker
import configparser 
import loguru
import os
import sys
import signal

# init 
loguru.logger.add("log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

# get if debug
config=configparser.ConfigParser()
config.read("config.ini")
g_debug=int(config["COMMON"]["debug"])

class APP(cmd.Cmd): 
    prompt = 'server>'
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
            self.woker=woker.Wroker(ip,port)
        except Exception as e:
            loguru.logger.error(e)
            sys.exit(1)

    def _check_arg(self,func,arg):
        if func=="cmd":
            if len(arg)==0:
                return False
            arg_list=arg.split(" ")
            if arg_list[0]=="kill" or arg_list[0]=="stop" or arg_list[0]=="start":
                if len(arg_list)!=2:
                    print(APP.RED+f"[-]  {func} {arg} client_ip:port"+APP.END)
                    return False
                client_list=self.woker.get_client()
                target=(arg_list[1].split(":")[0],int(arg_list[1].split(":")[1]))
                if target in client_list:
                    return True
                else:
                    print(APP.RED+"[-]  client not exist"+APP.END)
                    return False
            elif arg_list[0]=="reload_config":
                if len(arg_list) > 3:
                    print(APP.RED+f"[-]  {func} client_ip:port [config_path]"+APP.END)
                    return False
                client_list=self.woker.get_client()
                target=(arg_list[1].split(":")[0],int(arg_list[1].split(":")[1]))
                if target in client_list:
                    return True
                else:
                    print(APP.RED+"[-]  client not exist"+APP.END)
                    return False
            else:
                return False
            

    def do_exit(self, arg):
        '''
        exit
        '''
        pid=os.getpid()
        os.kill(pid,signal.SIGTERM)

    def do_get_client(self, arg):
        '''
        get client list, no param
        '''
        global g_debug
        client_list=self.woker.get_client()
        if g_debug:
            loguru.logger.info(f"client_list: {client_list}")
        if len(client_list)==0:
            print(APP.RED+"[-]  no client"+APP.END)
        for client in client_list:
            # if g_debug:
            #     print(type(client))
            addr=(client[0],client[1])
            status=self.woker.get_client_status(addr)
            if status=="stop":
                print(APP.BLUE+"[+] <client_info> "+str(client[0])+"  "+str(client[1])+" "+status+APP.END)
                continue
            print(APP.GREEN+"[+] <client_info> "+str(client[0])+"  "+str(client[1])+" "+status+APP.END)

    def do_get_client_num(self, arg):
        '''
        get client number,no param
        '''
        client_num=self.woker.get_client_num()
        print(client_num)

    def do_cmd(self, arg):
        '''
        send command to client
        prompt:
            server> cmd <client_ip:port> <command>
        <command>:
            kill: kill the client,for example: server> cmd kill client_ip:port
            stop: stop the client,for example: server> cmd stop client_ip:port
            start: start the client,for example: server> cmd run client_ip:port
        '''
        if not self._check_arg("cmd",arg):
            print(APP.RED+"[-]  cmd error"+APP.END)
            return
        cmd=arg.split(" ")[0]
        addr=arg.split(" ")[1]
        # todo reload_config
        if cmd=="reload_config":
            if len(arg.split(" "))==3:
                config_path=arg.split(" ")[2]
                ret=self.woker.send_cmd(cmd,addr,config_path)
            else:
                ret=self.woker.send_cmd(cmd,addr)
                
        else:
            ret=self.woker.send_cmd(cmd,addr)
        
        if ret[0]:
            print(APP.GREEN+"[+]  run success"+APP.END)
            if ret[1]!=None:
                print(APP.GREEN+"[+]  ret: "+ret[1]+APP.END)
            else:
                print(APP.GREEN+"[+]  ret: is None"+APP.END)
        else:
            print(APP.RED+"[-]  run fail"+APP.END)
        
        ip=addr.split(":")[0]
        port=int(addr.split(":")[1])
        if cmd=="stop":
            self.woker.set_client_status((ip,port),"stop")
        elif cmd=="start":
            self.woker.set_client_status((ip,port),"running")
        

    def do_get(self, arg):
        '''
        get info from elasticsearch
        prompt:
            server> get info_num
            server> get vuls_num
        '''
        if arg=="info_num":
            size=self.woker.get_es_info_num()
            print(APP.GREEN+f"[+]  info_num: {size}"+APP.END)
        elif arg=="vuls_num":
            size=self.woker.get_es_vuls_num()
            print(APP.GREEN+f"[+]  vuls_num: {size}"+APP.END)
        else:
            print(APP.RED+"[-]  get error"+APP.END)
            
    def do_delete(self, arg):
        '''
        delete info from elasticsearch
        prompt:
            server> delete info
            server> delete vuls
        '''
        if self.woker.delete_es_index(arg):
            print(APP.GREEN+"[+]  delete success"+APP.END)
        else:
            print(APP.RED+"[-]  delete fail"+APP.END)



if __name__ == "__main__":
    app=APP()
    app.cmdloop()
