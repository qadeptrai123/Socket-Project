from socket import *
import server_lib
from server_lib.util import *
from threading import Thread
import sys
import globals
from server_lib.connection import *
from server_lib.util import *
import lib

LOG = lib.LOG

addresses = {}

def main():
    
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    BUFSIZ = globals.SERVER_BUFSIZ
    # print(HOST, PORT, BUFSIZ)
    ADDR = (HOST, PORT)
    try:
        SERVER = socket(AF_INET, SOCK_STREAM)
        SERVER.bind(ADDR)
        LOG.info("Server started.")

        SERVER.listen(5)
        LOG.info("Waiting for connection...")
        ACCEPT_THREAD = Thread(target=accept_incoming_connections, args=(SERVER, addresses))
        
        ACCEPT_THREAD.start()
        ACCEPT_THREAD.join()
    except KeyboardInterrupt:
        LOG.info("Server stopped.")
    except Exception as e:
        LOG.error(f"Error: {e}")
    finally:
        SERVER.close()

        
if __name__ == "__main__":
    main()