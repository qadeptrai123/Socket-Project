from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
from lib.lib import *
import os
import lib

# def handshake(connection, target_address: tuple):
#     PUBLIC_KEY = connection.recvfrom(450)[0]
#     cipher_rsa = PKCS1_OAEP.new(RSA.import_key(PUBLIC_KEY))

#     # Tạo khóa AES và mã hóa bằng khóa công khai RSA của server
#     AES_KEY = get_random_bytes(16)
#     encrypted_aes_key = cipher_rsa.encrypt(AES_KEY)
#     connection.sendto(encrypted_aes_key, target_address)
#     return AES_KEY

LOG = lib.LOG

def disconnect(connection, HOST, PORT, SERVER_ADDR):
    while True:
        connection.sendto(create_packet("", HOST, PORT, 'Q'), SERVER_ADDR)
        
        connection.settimeout(15)
        try:
            header, _ = connection.recvfrom(2048)
        except Exception as e:
            LOG.error(f"Error: {e}")
            continue
        # header = decrypt_packet(header, AES_KEY)
        protocol_name, sender_ip, sender_port, type_request, content_length, data = J97P_parse(header)
        # data, _ = connection.recvfrom(content_length)
        # data = decrypt_packet(data, AES_KEY)
        if data == b'ACK':
            LOG.info("Disconnected from server.")
            connection.settimeout(None)        
            connection.close()
            return