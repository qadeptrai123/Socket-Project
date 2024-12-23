from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import hashlib
from Crypto.Util.number import bytes_to_long, long_to_bytes
import os


def ip_to_bytes(ip):
    if ip == 'localhost':
        ip = '127.0.0.1'
    return bytes(map(int, ip.split('.')))

def int_to_ip(n):
    return inet_ntoa(n.to_bytes(4, byteorder='big'))

def fill_zero(data, n):
    if len(data) < n:
        # Thêm byte 0 vào cuối để đủ n bytes
        data = data.ljust(n, b'\0')
   
    return data


def create_packet(data, ip, port, type): 
    
    # print(ip, port)
    protocol_name = b'J97P'  # Định dạng protocol name (4 byte)
    sender_ip = fill_zero(ip_to_bytes(ip), 4)  # Địa chỉ IP (4 byte)
    sender_port = long_to_bytes(port, 2)  # Port (2 byte)
    type_request = type.encode('utf-8')[:1]  # Loại request (1 byte)
    content = data if isinstance(data, bytes) == True else data.encode('utf-8')  # Nội dung (n bytes)
    # encrypted_content = encrypt_packet(content, AES_KEY)
    content_length = long_to_bytes(len(content), 4)  # Độ dài nội dung (4 byte)
    header = protocol_name + sender_ip + sender_port + type_request + content_length
   
    # Tạo gói tin
    packet = header + content
    return fill_zero(packet, 2048) # (header = 15 bytes) + content + 0-bytes padding = 2048 bytes

def create_packet_udp(data, chunk_id): 
    
    # print(ip, port)
    protocol_name = b'GUDP'  # Định dạng protocol name (4 byte)
    # encrypted_content = encrypt_packet(content, AES_KEY)
    chunk_id = long_to_bytes(chunk_id, 4)  # Chunk ID (4 byte)
    checksum = calculate_hash_sha256_checksum(data)
    content_length = long_to_bytes(len(data), 4)  # Độ dài nội dung (4 byte)
    header = protocol_name + chunk_id + checksum + content_length
   
    # Tạo gói tin
    packet = header + data
    return fill_zero(packet, 2048) # (header = 8 bytes) + content + 0-bytes padding = 2048 bytes

def calculate_hash_sha256_checksum(data: bytes):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.digest()

def calculate_hash_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:  # Mở tệp ở chế độ đọc nhị phân
            while chunk := f.read(8192):  # Đọc tệp theo từng khối (8192 byte mỗi lần)
                sha256_hash.update(chunk)  # Cập nhật hash với khối dữ liệu
        return {'sum': sha256_hash.hexdigest(), 'code': 0}  # Trả về mã hash dạng chuỗi hex
    except FileNotFoundError:
        return {'sum': '', 'code': -1}  # Trả về mã hash rỗng nếu không tìm thấy tệp
    except Exception as e:
        return {'sum': '', 'code': -2}  # Trả về mã hash rỗng nếu có lỗi xảy ra

# def decrypt_packet(packet, key):
#     nonce = packet[:16]
#     cipher_aes = AES.new(key, AES.MODE_EAX, nonce=nonce)
#     ciphertext = packet[16:]
#     plaintext = cipher_aes.decrypt(ciphertext)
#     return plaintext

# def encrypt_packet(packet, key):
#     if isinstance(packet, str):
#         packet = packet.encode()
#     cipher_aes = AES.new(key, AES.MODE_EAX)
#     nonce = cipher_aes.nonce
#     ciphertext, tag = cipher_aes.encrypt_and_digest(packet)
#     return nonce + ciphertext

def J97P_header_parse(header):
    protocol_name = header[:4].decode('utf-8')
    sender_ip = bytes_to_long(header[4:8])
    sender_port = int.from_bytes(header[8:10], byteorder='big')
    type_request = header[10:11].decode('utf-8')
    content_length = int.from_bytes(header[11:15], byteorder='big')
    return protocol_name, sender_ip, sender_port, type_request, content_length


def J97P_parse(packet):
    header = packet[:15]
    protocol_name, sender_ip, sender_port, type_request, content_length = J97P_header_parse(header)
    content = packet[15:content_length+15]
    return protocol_name, sender_ip, sender_port, type_request, content_length, content


def GUDP_parse(packet):
    protocol_name = packet[:4]
    chunk_id = int.from_bytes(packet[4:8], byteorder='big')
    checksum = packet[8:40]
    content_length = int.from_bytes(packet[40:44], byteorder='big')
    content = packet[44:content_length+44]
    return protocol_name, chunk_id, checksum, content_length, content


def are_files_identical(file_path1, file_path2):
    """
    Check if two binary files are identical.

    :param file_path1: Path to the first file
    :param file_path2: Path to the second file
    :return: True if files are identical, False otherwise
    
    """
    with open(file_path1, 'rb') as file1, open(file_path2, 'rb') as file2:
        while True:
            chunk1 = file1.read(4096)
            chunk2 = file2.read(4096)
            if chunk1 != chunk2:
                return False
            if not chunk1:  # End of file
                break
        return True # Files are identical    
            
import hashlib

def calculate_checksum(file_path):
    """
    Calculate the SHA-256 checksum of a file.

    :param file_path: Path to the file
    :return: SHA-256 checksum as a hexadecimal string
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()


def are_checksums_identical(file_path1, file_path2):
    """
    Check if the SHA-256 checksums of two files are identical.

    :param file_path1: Path to the first file
    :param file_path2: Path to the second file
    :return: True if checksums are identical, False otherwise
    """
    checksum1 = calculate_checksum(file_path1)
    print(f"checksum of file 1: {checksum1}")
    checksum2 = calculate_checksum(file_path2)
    print(f"checksum of file 2: {checksum2}")
    return checksum1 == checksum2