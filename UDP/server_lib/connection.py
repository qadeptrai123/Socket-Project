from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
import globals
import os
from server_lib.util import *
from lib.lib import *

def accept_client(server_socket: socket, addresses: dict):  # address is a dictionary
    """Sets up handling for incoming clients."""
    LOG = lib.LOG
    while True:
        try:
            data, client_address = server_socket.recvfrom(2048)
            # LOG.info(f"Accepted connection from {client_address}")
            # addresses[client_address[0]] = client_address[1]
            # num = ("127.0.0.1", 1111)
            # server_socket.setblocking(True) 
            Thread(target=handle_client, args=(server_socket, client_address, data)).start()
        except Exception as e:
            LOG.error(f"Error: {e}")
            break
        

