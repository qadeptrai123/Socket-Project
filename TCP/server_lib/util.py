from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.number import bytes_to_long, long_to_bytes
from threading import Thread
from lib.lib import *
import os
import lib
import globals
import lib.log
import json
import time
import select

def flush_socket_buffer(sock):
    """ Đọc hết dữ liệu trong bộ đệm socket nếu có dữ liệu chưa được đọc """
    try:
        # Đọc hết tất cả dữ liệu trong bộ đệm của socket (vì recv chỉ đọc một phần bộ đệm)
        sock.setblocking(0)  # Đặt socket ở chế độ non-blocking
        while True:
            data = sock.recv(1024)  # Đọc dữ liệu 1024 byte mỗi lần
            if not data:
                break  # Nếu không có dữ liệu nữa thì thoát vòng lặp
    except Exception as e:
        print(f"Lỗi khi làm sạch bộ đệm socket: {e}")

def getFiles(directory):
    files = [
        {'name': f, 'size': os.path.getsize(os.path.join(directory, f))}
        for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    return files

def checkExistFile(file_name):
    return os.path.exists(os.path.join('database', file_name))

def getFileSize(file_name):
    return os.path.getsize(os.path.join('database', file_name))

def handle_client(connection, a, SERVER):
    LOG = lib.LOG
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    # connection.settimeout(5)
    # try:
    connection.setblocking(True)
    # connection.settimeout(5)
    
    while True:
        connection.settimeout(15)
        try:
            data = recvall(connection, 15)
            # data = decrypt_packet(data)
            protocol_name, sender_ip, sender_port, type_request, payload_length = J97P_header_parse(data)
            payload = recvall(connection, payload_length)
            # payload = decrypt_packet(payload)
            ok = 1
        except Exception as e:
            continue
        if type_request == 'K':
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Keep Alive[/bold magenta]" , extra={"markup": True})
            connection.sendall(create_packet('ACK', HOST, PORT, 'R', connection))
        elif type_request == 'F':
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Get files list[/bold magenta]" , extra={"markup": True})
            files_list = json.dumps(getFiles('database'))
            connection.sendall(create_packet(files_list, HOST, PORT, 'R', connection))
        elif type_request == 'D':
            payload = json.loads(payload.decode())
            file_name = payload['file_name']
            offset = payload['offset']
            length = payload['length']
            chunk_index = payload['chunk_index']
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name} Part {chunk_index} [/green]" , extra={"markup": True})
            
            file_path = os.path.join('database', file_name)
            bytes_readed = 0
            # LOG.info(length)
            with open(file_path, 'rb') as f:
                f.seek(offset)
                # LOG.info("start")
                while bytes_readed < length:
                    # LOG.info(bytes_readed)
                    data = f.read(min(1024, length - bytes_readed))
                    # packet = encrypt_packet
                    connection.sendall(create_packet_tcp(data, HOST, PORT, b'D', connection))
                    # connection.sendall(data)
                    bytes_readed += len(data)
                    # header_ACK = connection.recv(8)
                    # # header_ACK = decrypt_packet(header_ACK)
                    # protocol_name, payload_length = GTCP_header_parse(header_ACK)
                    # payload_ACK = connection.recv(payload_length)
                    # # payload_ACK = decrypt_packet(payload_ACK)
                    # if payload_ACK != b'ACK':
                    #     LOG.error(f"Error: {payload_ACK}")
                    #     break
                    
                # LOG.info("end")
                # connection.sendall(b'EOF')
                connection.sendall(create_packet_tcp(b'EOF', HOST, PORT, b'D', connection))
        elif type_request == 'Q':
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Quit[/bold magenta]" , extra={"markup": True})
            connection.sendall(create_packet('ACK', HOST, PORT, 'R', connection))
            break
            # LOG.info("pp")
        
        # connection.sendall(encrypt_packet(create_packet('', HOST, PORT, 'S', connection)))
        # LOG.info("kkk")
        
        elif type_request == 'E':
            
            # LOG.info(payload)
            payload = json.loads(payload.decode())
            file_name = payload['file_name']
            chunk_number = payload['chunk_number']
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name}[/green] [bold magenta]| Number of chunk:[/bold magenta] [green]{chunk_number}[/green]" , extra={"markup": True})
            exist_file = checkExistFile(file_name)
            if exist_file:
                file_size = getFileSize(file_name)
                res = {
                    'response': 'Y',
                    'file_size': file_size,
                    'checksum': calculate_hash_sha256(os.path.join('database', file_name))['sum']
                }
                connection.sendall(create_packet(json.dumps(res), HOST, PORT, 'R', connection))
            else:
                res = {
                    'response': 'N'
                }
                connection.sendall(create_packet(json.dumps(res), HOST, PORT, 'R', connection))    
        # for chunk_index in range(1, 4):
        #     _c, _a = connection.accept()
        # for chunk_index in range(1, 4):
        #     _c, _a = connection.accept()
    
    # except Exception as e:
    #     LOG.error(f"Error: {e}, {connection}")
    # finally:
    #     LOG.info(f"{int_to_ip(sender_ip)}:{sender_port} disconnected")
    #     connection.close()
    
            
     
        
        
def generate_RSA_key():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key
