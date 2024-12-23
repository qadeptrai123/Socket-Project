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
from collections import deque

LOG = lib.LOG

def flush_socket_buffer(sock):
    """ Đọc hết dữ liệu trong bộ đệm socket nếu có dữ liệu chưa được đọc """
    try:
        # Đọc hết tất cả dữ liệu trong bộ đệm của socket (vì recv chỉ đọc một phần bộ đệm)
        sock.setblocking(0)  # Đặt socket ở chế độ non-blocking
        while True:
            data, _ = sock.recvfrom(1024)  # Đọc dữ liệu 1024 byte mỗi lần
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


def handle_send_file(connection, chunk_size, file_name, offset, length, client_address):
 
    file_path = os.path.join('database', file_name)
    bytes_readed = 0
    # return
    # continue
    WINDOW_SIZE = 32
    with open(file_path, 'rb') as f:
        f.seek(offset) #find for offset
        chunk_id = 0
        window = deque(maxlen=WINDOW_SIZE)
        last_ack = -1
        # LOG.info("Start send")
        while bytes_readed < length or window:
            # time.sleep(1)
            # LOG.info(f"Bytes readed: {bytes_readed}, Length: {length}")
            while len(window) < WINDOW_SIZE and bytes_readed < length:
                # LOG.info(len(window))
                # time.sleep(0.1)
                data = f.read(min(1024, length - bytes_readed))
                packet = create_packet_udp(data, chunk_id)
                connection.sendto(packet, client_address)
                window.append((packet, chunk_id))
                chunk_id += 1
                bytes_readed += len(data)
            # LOG.info(f"Bytes readed: {bytes_readed}, Length: {length}")
            try:
                connection.settimeout(3)
                data, client_address = connection.recvfrom(2048)
                protocol_name, ack_number, checksum, content_length, content = GUDP_parse(data)
                
                while window and window[0][1] <= ack_number:
                    window.popleft()
                    last_ack = ack_number 
            except:
                LOG.info(f"[bold red]Timeout[/bold red] Chunk {last_ack} not received", extra={"markup": True})
                for packet, ack_number in window:
                    # LOG.info(f"Resend chunk {ack_number}")
                    connection.sendto(packet, client_address)
                # LOG.info(bytes_readed)
                
            
        while True:
            connection.sendto(create_packet_udp(b'EOF', chunk_id+1), client_address)
            try:
                connection.settimeout(5)
                data, client_address = connection.recvfrom(2048)
                protocol_name, ack_number, checksum, content_length, content = GUDP_parse(data)
                if ack_number == chunk_id + 1:
                    break
            except:
                continue    
        # connection.sendto(create_packet(file_path, HOST, PORT, 'W'), client_address)
        # LOG.info("End send")
def handle_client(connection : socket, client_address : tuple):
    LOG = lib.LOG
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    connection.setblocking(True) 
    while True:
        connection.settimeout(25)
        # if(data_code == b''):
            # connection.settimeout(15)
        try:
            data, client_address = connection.recvfrom(2048) #top

            protocol_name, sender_ip, sender_port, type_request, payload_length, payload = J97P_parse(data)
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Type request:[/bold magenta] [green]{type_request}[/green]" , extra={"markup": True})
        except Exception as e:
            LOG.info("[magenta]Waiting for request from client...[/magenta]", extra={"markup": True})
            continue
        # else:
        #     protocol_name, sender_ip, sender_port, type_request, payload_length, payload = J97P_parse(data_code)
        
            data_code = b''
        
        if type_request == 'F':
            connection.settimeout(25)
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Get files list[/bold magenta]" , extra={"markup": True})
            files_list = json.dumps(getFiles('Database'))
           # send file list 
            LOG.info(f"[bold green][{protocol_name}][/bold green] Send files list to {int_to_ip(sender_ip)}:{sender_port}" , extra={"markup": True})
            connection.sendto(create_packet(files_list, HOST, PORT, 'R') , client_address)
        elif type_request == 'D':
            
            connection.settimeout(25)
            payload = json.loads(payload.decode())
            file_name = payload['file_name']
            offset = payload['offset']
            length = payload['length']
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name} [/green]" , extra={"markup": True})
            
            handle_send_file(connection, 1024, file_name, offset, length, client_address)
        elif type_request == 'E':
            connection.settimeout(25)
            payload = json.loads(payload.decode())
            file_name = payload['file_name']
            chunk_number = payload['chunk_number']
            LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name}[/green]" , extra={"markup": True})
            exist_file = checkExistFile(file_name)
            if exist_file:
                file_size = getFileSize(file_name)
                res = {
                    'response': 'Y',
                    'file_size': file_size,
                    'checksum': calculate_hash_sha256(os.path.join('database', file_name))['sum']
                }
                # LOG.info(res)
                connection.sendto(create_packet(json.dumps(res), HOST, PORT, 'R'), client_address)
            else:
                res = {
                    'response': 'N'
                }
                connection.sendto(create_packet(json.dumps(res), HOST, PORT, 'R'), client_address)    
        # for chunk_index in range(1, 4):
        #     _c, _a = connection.accept()
        # for chunk_index in range(1, 4):
        #     _c, _a = connection.accept()
    
    # except Exception as e:
    #     LOG.error(f"Error: {e}, {connection}")
    # finally:
    #     LOG.info(f"{int_to_ip(sender_ip)}:{sender_port} disconnected")
    #     connection.close()
    
# def client_thread(connection):
    
#     try:
#         handle_client(connection)
#     except Exception as e:
#         LOG.error(f"Error in client thread: {e}")
#     finally:
#         connection.close()
   
        
# def generate_RSA_key():
#     key = RSA.generate(2048)
#     private_key = key.export_key()
#     public_key = key.publickey().export_key()
#     return public_key, private_key
