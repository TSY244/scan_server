import cmd
import cmd_tools.woker as woker
import configparser 
import loguru

# init 
loguru.logger.add("log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

# get if debug
config=configparser.ConfigParser()
config.read("config.ini")
g_debug=config["COMMON"]["debug"]



class APP(cmd.Cmd): 
    prompt = 'server>'
    RED="\033[0;31;40m"
    GREEN="\033[0;32;40m"
    END="\033[0m"
    def __init__(self,ip,port):
        '''
        param:
            ip: server ip
            port: server port
        '''
        super().__init__()
        self.woker=woker.Wroker(ip,port)

    def _check_arg(self,func,arg):
        if func=="cmd":
            if len(arg)==0:
                return False
            arg_list=arg.split(" ")
            if arg_list[0]=="kill":
                if len(arg_list)!=2:
                    print(APP.RED+"[-]  kill client_ip:port"+APP.END)
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
            
    def do_get_client(self, arg):
        '''
        get client list, no param
        '''
        client_list=self.woker.get_client()
        if g_debug:
            loguru.logger.info(f"client_list: {client_list}")
        if len(client_list)==0:
            print(APP.RED+"[-]  no client"+APP.END)
        for client in client_list:
            if g_debug:
                print(type(client))
            print(APP.GREEN+"[+] <client_info> "+str(client[0])+"  "+str(client[1])+APP.END)

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
        '''
        if not self._check_arg("cmd",arg):
            print(APP.RED+"[-]  cmd error"+APP.END)
            return
        self.woker.send_cmd(arg)






if __name__ == "__main__":
    app=APP()
    app.cmdloop()
