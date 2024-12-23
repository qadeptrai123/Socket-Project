from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
import globals
import os
from server_lib.util import *
from lib.lib import *

def accept_incoming_connections(SERVER, addresses):
    """Sets up handling for incoming clients."""
    LOG = lib.LOG
    while True:
        try:
            client, client_address = SERVER.accept()
            # AES_KEY = handshake(client, PUBLIC_KEY, PRIVATE_KEY)
            LOG.info("One socket created to handle client.")
            addresses[client] = client_address
            Thread(target=handle_client, args=(client, client_address, SERVER)).start()
        except Exception as e:
            print("Error: ", e)
            
# def handshake(client):
#     # Gửi khóa công khai RSA cho client
#     client.sendall(public_key)
    
#     # Nhận khóa AES đã mã hóa từ client
#     encrypted_aes_key = client.recv(256)
#     cipher_rsa = PKCS1_OAEP.new(RSA.import_key(private_key))
#     aes_key = cipher_rsa.decrypt(encrypted_aes_key)
#     # print("AES key received and decrypted from port ", client.getpeername()[1])
#     return aes_key

