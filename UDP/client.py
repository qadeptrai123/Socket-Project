from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os
from client_lib.util import *
from client_lib.connection import *
import sys
import lib
from lib.lib import *
from lib.log import *
import globals
from client_lib.util import *
import json


LOG = lib.LOG

CLIENT_HOST = globals.CLIENT_HOST  
CLIENT_PORT = globals.CLIENT_PORT
print(CLIENT_HOST, CLIENT_PORT)

def main():
    #prepare client and server
    HOST = globals.SERVER_HOST    
    PORT = globals.SERVER_PORT
    BUFSIZ = globals.SERVER_BUFSIZ
    SERVER_ADDR = (HOST, PORT) 
    CLIENT_ADDR = (CLIENT_HOST, CLIENT_PORT)
    
    #bind client port
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.setsockopt(SOL_SOCKET, SO_RCVBUF, 1048576)
    client_socket.bind(CLIENT_ADDR)
    # CLIENT_HOST, CLIENT_PORT = client_socket.getsockname()
        
    # client_socket.sendto(b"hello", SERVER_ADDR)    

    #code below
    try:
        files_list = getFileList(client_socket, CLIENT_HOST, CLIENT_PORT)
        
        
        #Test below
        
        #---------------------------------------
        # LOG.info(files_list)
        #---------------------------------------
        
        #ask for file list 
        #---------------------------------------------------
        if files_list == -1:
            LOG.error("Failed to get file list from server.")
            return
        elif files_list["type_request"] == "R":
            files_list = json.loads(files_list['data'].decode())

        
        msg_files_list = "[magenta]Files in server database:[/magenta]\n" + "\n".join([f"[green]{f['name']}[/green] - {f['size'] // (1024**2) } MB" for f in files_list])
        LOG.info(msg_files_list, extra={"markup": True})
        #---------------------------------------------------
        # return
        #interact with server

        handle_process(client_socket, CLIENT_HOST, CLIENT_PORT)
        
    except KeyboardInterrupt:
        LOG.info("[bold red]Exiting...[/bold red]", extra={"markup": True})
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()