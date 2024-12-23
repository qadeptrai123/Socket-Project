from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
from lib.lib import *

def handshake(connection):
    PUBLIC_KEY = connection.recv(450)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(PUBLIC_KEY))

    # Tạo khóa AES và mã hóa bằng khóa công khai RSA của server
    AES_KEY = get_random_bytes(16)
    IV = get_random_bytes(16)       # 16 bytes cho chế độ CBC
    encrypted_aes_key = cipher_rsa.encrypt(AES_KEY)
    connection.sendall(encrypted_aes_key)
    connection.sendall(IV)
    return AES_KEY

def disconnect(connection, HOST, PORT):
    while True:
        connection.sendall(create_packet("", HOST, PORT, 'Q', connection))
        header = recvall(connection, 15)
        # header = decrypt_packet(header)
        protocol_name, sender_ip, sender_port, type_request, content_length = J97P_header_parse(header)
        data = recvall(connection, content_length)
        # data = decrypt_packet(data)
        if data == b'ACK':
            connection.close()
            return