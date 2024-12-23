from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
import lib
from lib.lib import *
import globals
from rich.progress import Spinner
import time
from rich.progress import Progress
import hashlib
import os
import sys
import time
import json
from client_lib.connection import *
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
directory = ''
# create_packet(data, ip, port, type)

CHUNK_NUMBER = globals.CHUNK_NUMBER


CLIENT_HOST = globals.CLIENT_HOST
CLIENT_PORT = globals.CLIENT_PORT
CLIENT_ADDR = (CLIENT_HOST, CLIENT_PORT)
        
        
SERVER_HOST = globals.SERVER_HOST
SERVER_PORT = globals.SERVER_PORT
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)

import os

def merge_file(file_name):
    # Tìm tên tệp mới nếu tệp đã tồn tại
    base_name, ext = os.path.splitext(file_name)
    file_path = os.path.join("download", file_name)
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join("download", f"{base_name}-{counter}{ext}")
        counter += 1

    with open(file_path, 'wb') as f:
        for i in range(CHUNK_NUMBER):
            chunk_path = os.path.join("download", file_name + f".part{i+1}")
            with open(chunk_path, 'rb') as chunk_f:
                f.write(chunk_f.read())
            os.remove(chunk_path)

    LOG.info(f"File merged and saved as {file_path}")

def download_chunk(client, file_name, offset, length, progress, task_id):
    LOG = lib.LOG
    # client = socket(AF_INET, SOCK_DGRAM)
    # client.bind((CLIENT_HOST, 0))  # Bind to any available port
    client_ip, client_port = client.getsockname()
    # return
    # LOG.info(f"[cyan]Client address: [green]{client_ip}:{client_port}[/]", extra={"markup": True})    
    payload = {
        'file_name': file_name,
        'offset': offset,
        'length': length,
    }
    
    client.sendto(create_packet(json.dumps(payload), client_ip, client_port, 'D'), SERVER_ADDR)
    # os.makedirs(os.path.dirname(download_path), exist_ok=True)
    if not os.path.exists("download"):
        os.makedirs("download")
    download_path = os.path.join("download", file_name)
    # Tạo thư mục nếu chưa tồn tại
    counter = 0
    while os.path.exists(download_path):
        counter += 1
        tokens = file_name.split('.')
        download_path = os.path.join("download", f"{tokens[0]}({counter}).{tokens[1]}" )
            
            
    # try:
    # LOG.info(f"[cyan]download_path {download_path}[/]", extra={"markup": True})
    # return
    
    
    with open(download_path, 'wb') as f:
        chunk_downloaded = 0
        # os.makedirs("chunk_error_tmp/" + file_name + f".part{chunk_index}", exist_ok=True)
        # with open("chunk_error_tmp/" + file_name + f".part{chunk_index}", 'wb') as error_file:
        #     pass
        # with open("chunk_error_tmp/" + file_name + f".part{chunk_index}", 'r+b') as error_file:
        expected_chunk_id = 0
        chunk_received = 0
        last_chunk_id = length // 1024
        # LOG.info(f"{file_name} - {length}")
        # LOG.info(f"Last chunk id: {last_chunk_id}")
        while True:
            # time.sleep(0.005)
            try:
                # time.sleep(1)
                client.settimeout(15)
                data, _ = client.recvfrom(2048)
                protocol_name, chunk_id, checksum, payload_length, payload = GUDP_parse(data)
                # LOG.info(f"Chunk {chunk_id} received")
                # LOG.info(f"data {data}")
                if payload == b'EOF':
                    # LOG.info(chunk_id)
                    client.sendto(create_packet_udp(b'ACK', chunk_id), SERVER_ADDR)
                    break
                if checksum != calculate_hash_sha256_checksum(payload):
                    continue
                # if chunk_id == last_chunk_id:
                #     LOG.info(f"Last chunk {chunk_id} received")
                
                if chunk_id == expected_chunk_id:
                    
                    chunk_downloaded = len(payload)
                    f.seek(chunk_id * 1024)
                    f.write(payload)
                    # x += chunk_downloaded
                    progress.update(task_id, advance=chunk_downloaded)
                    expected_chunk_id += 1
                    chunk_received += 1
                    # LOG.info(chunk_downloaded)
                    if chunk_received % 32 == 0 or chunk_id == last_chunk_id:
                        ack_packet = create_packet_udp(b'ACK', chunk_id)
                        client.sendto(ack_packet, SERVER_ADDR)
                # if resend == b'N':
            except:
                continue
    # os.remove("chunk_error_tmp/" + file_name + f".part{chunk_index}")
    # disconnect(client, client_ip, client_port, SERVER_ADDR)
    # LOG.info(x)
    return 1, download_path
    # return -1 # cannot download the chunk

def download_file(connection, client_ip, client_port, file_name):
    LOG = lib.LOG
    payload = {
        'file_name': file_name,
        'chunk_number': CHUNK_NUMBER
    }
    connection.settimeout(5)
    connection.sendto(create_packet(json.dumps(payload), client_ip, client_port, 'E'), SERVER_ADDR)

    data_packet, _ = connection.recvfrom(2048)
    protocol_name, sender_ip, sender_port, type_request, payload_length, payload = J97P_parse(data_packet)
    payload = json.loads(payload.decode())
    #-----------------------------
    # payload = {
    #     'response': payload['response'],
    #     'file_size': payload['file_size']
    # }
    # datatype : dictionary -> same as map in c++
    #-----------------------------
    response = payload['response']
    if response == 'N':
        return -1
    elif response == 'Y':
        threads = []
        file_size = payload['file_size']

        LOG.info(f"[cyan]Downloading file: [green]{file_name}[/] - {file_size // (2**20)} MB[/cyan]", extra={"markup": True})   
    # LOG.info(f"     File size: {file_size}")
        chunk_size = (file_size + CHUNK_NUMBER - 1) // CHUNK_NUMBER #bytes per chunk
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
        try:
            download_path = os.path.join("download", file_name)
            with progress:
                tasks_id = []
                length = file_size
                task_id = progress.add_task(f"{file_name.rjust(13)}", total=length)
                tasks_id.append(task_id)
                # gửi 1 gói tin 5 lần cho mỗi chunk
                # for _ in range(1):
                #     LOG.info("[cyan] Hear+_+[/cyan]")
                _, download_path = download_chunk(connection, file_name, 0, length, progress, task_id)
                
                    # break
                    
                # for i in range (CHUNK_NUMBER):
                #     offset = chunk_size * i  # i = 0, 1, 2, 3
                #     length = min(chunk_size, file_size - offset)
                #     chunk_path = os.path.join("download", file_name + f".part{i+1}")
                #     while not os.path.exists(chunk_path) or os.path.getsize(chunk_path) < length:
                #         LOG.warning(f"Chunk {i+1} is not downloaded completely. Redownloading...")
                #         # xoá đi chunk tải không hoàn thiện
                #         if os.path.exists(chunk_path):
                #             os.remove(chunk_path)
                #         thr = Thread(target=download_chunk, args=(file_name, offset, length, i+1, progress, tasks_id[i]))
                #         time.sleep(1)     
                
            # merge_file(file_name)  
            # LOG.info("Done download file")
            if calculate_hash_sha256(download_path)['sum'] != payload['checksum']:
                return -2
        except Exception as e:
            return -2
    connection.settimeout(None)
    return 1
    
    # CHUNK_NUMBER = globals.CHUNK_NUMBER
    # threads = [
    #     Thread(target=download_chunk, args=(file_name, offset, i))
    #     for i in range(CHUNK_NUMBER)
    # ]
    # tasks = [
    #     {"desc": f"Downloading chunk {i+1}", "duration": 1}
    #     for i in range(CHUNK_NUMBER)
    # ]
    # task_ids = [
    #     progress.add_task(task["desc"], total=100) for task in tasks
    # ]
        
def msg_found_file(files_list):
    if len(files_list) == 0:
        return '[magenta]No file found in your input.txt[/]'
    msg = '[magenta]Found file in your input.txt:[/]\n'
    for i in range(len(files_list)):
        msg = msg + f'{i+1}. [green]{files_list[i]}[/]\n'
    return msg

def getFirstChecking(file_path):
    files_list = []
    line = 0
    with open(file_path, 'r') as f:
        files = f.readlines()
        for file in files:
            line += 1
            file = file.strip()
            files_list.append(file)
    return files_list, line

def detect_file_change(file_path, current_line, sha256):
    files_list = []
    new_sha256 = calculate_hash_sha256(file_path)
    if new_sha256 != sha256:
        new_files_list, new_current_line = getFirstChecking(file_path)
        files_list = new_files_list[current_line:]
        current_line = new_current_line
    return files_list, current_line, new_sha256

# I fixed some cases of LOG.info in this function - Khuong 
def handle_process(connection, client_ip, client_port):
    LOG = lib.LOG
    CONSOLE = lib.CONSOLE
    files_list = []
    current_line = 0
    sha256 = -1
    if not os.path.exists("input.txt"):
        with open("input.txt", 'w') as f:
            pass
    with CONSOLE.status("[cyan]First checking your input.txt...") as status:
        spinner = Spinner("circle") # Chọn loại spinner, có thể là "circle", "dots", "star", ...
        file_path = os.path.join(directory, 'input.txt')
        # print(file_path)
        sha256 = calculate_hash_sha256(file_path)
        files_list, current_line = getFirstChecking(file_path)
        time.sleep(2)

    # current_number_of_files = len(files_list)
    LOG.info(msg_found_file(files_list), extra={"markup": True})
    while True:
        if len(files_list):
            # if(len(files_list) > current_number_of_files):
            LOG.info("[cyan]Found changes in your input.txt:[/]", extra={"markup": True})
            for file in files_list:
                LOG.info(f"  [green]{file}[/]", extra={"markup": True})
            LOG.info("[cyan]Starting download files...[/]", extra={"markup": True})
            for i in range(len(files_list)):
                while True:
                    file_name = files_list[i]
                    response = download_file(connection, client_ip, client_port, file_name)
                    if response == 1:
                        LOG.info(f"[green]Downloaded file {file_name} successfully[/]", extra={"markup": True})
                        break
                    elif response == -1:
                        LOG.error(f"[red]File {file_name} not found on server[/]", extra={"markup": True})
                        break
                    else:
                        LOG.error(f"[red]Failed to download file {file_name}[/]", extra={"markup": True})
                        LOG.info("[cyan]Retrying...[/]", extra={"markup": True})
                
            LOG.info("[magenta]All files are downloaded[/magenta]", extra={"markup": True})
        else:
            LOG.info("[cyan]No file found in your input.txt. Waiting for changes...[/]", extra={"markup": True})
        time.sleep(5)
        files_list, current_line, sha256 = detect_file_change(file_path, current_line, sha256) 
    
    # disconnect(connection, client_ip, client_port, aes_key)
    
        # with CONSOLE.status("[cyan]Scanning changes in your input.txt...") as status:
        #     spinner = Spinner("circle")  # Chọn loại spinner, có thể là "circle", "dots", "star", ...
        #     for _ in range(10):
        #         time.sleep(0.1)
                # spinner.next()
                
            
        
    # except Exception as e:
    #     LOG.error(f"Error: {e}")

        
def getFileList(connection : socket, client_ip, client_port):
    LOG = lib.LOG
    connection.settimeout(5)
    try:
        LOG.info(f"[cyan]Requesting file list from server...[/]", extra={"markup": True})
        connection.sendto(create_packet("", client_ip, client_port, 'F'), SERVER_ADDR)
        header, _ = connection.recvfrom(2048)
        protocol_name, sender_ip, sender_port, type_request, content_length, content = J97P_parse(header)
    except socket.timeout:
        LOG.error("Connection timed out.")
        return -1
    except Exception as e:
        LOG.error(f"An error occurred: {e}")
        return -1
    return {
        'protocol_name': protocol_name,
        'sender_ip': sender_ip,
        'sender_port': sender_port,
        'type_request': type_request,
        'content_length': content_length,
        'data': content 
    }