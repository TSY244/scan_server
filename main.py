import server
import configparser
import loguru
import sys
import signal
import tools.cmd_tools.cmd_tools as mycmd
import os


# init loguru
loguru.logger.add("log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

# init signal
def signal_handler(signal, frame):
    loguru.logger.info("You pressed Ctrl+C!")
    pid=os.getpid()
    os.kill(pid,signal)
    
def get_mode():
    config = configparser.ConfigParser()
    config.read('config.ini')
    mode = config['COMMON']['mode']
    return mode
    


def main():
    mode=get_mode()
    if mode == "0":
        server.main()
    elif mode == "1":
        app=mycmd.APP("0.0.0.0",9999)
        app.cmdloop()
    else:
        loguru.logger.error("mode error")
        sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()