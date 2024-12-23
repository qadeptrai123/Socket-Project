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
    ADDR = (HOST, PORT)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(ADDR)
    server_socket.setsockopt(SOL_SOCKET, SO_SNDBUF, 1048576)
    # try:
    LOG.info("Server started.")
    # accept_client(server_socket, addresses)
    handle_client(server_socket, addresses)
    # except KeyboardInterrupt:
    #     LOG.info("Server stopped.")
    # except Exception as e:
    #     LOG.error(f"Error: {e}")
    # finally:
    #     server_socket.close()

        
if __name__ == "__main__":
    main()
