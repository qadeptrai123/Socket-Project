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
    
def main():
    try:
        HOST = globals.SERVER_HOST
        PORT = globals.SERVER_PORT
        
        LOG.info(f"Connecting to server at {HOST}:{PORT}")
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((HOST, PORT))
        # AES_KEY, IV = handshake(connection)
        
        client_ip, client_port = connection.getsockname()
        files_list = getFileList(connection, client_ip, client_port)
        
        files_list = json.loads(files_list['data'].decode())

        msg_files_list = "[magenta]Files in server database:[/magenta]\n" + "\n".join([f"[green]{f['name']}[/green] - {f['size'] // (1024**2) } MB" for f in files_list])
        LOG.info(msg_files_list, extra={"markup": True})

        handle_process(connection, client_ip, client_port)
    except KeyboardInterrupt:
        LOG.info("Exiting...")
    finally:
        disconnect(connection, client_ip, client_port)

if __name__ == "__main__":
    main()