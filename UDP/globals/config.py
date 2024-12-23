import configparser



def get_config():
    global SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ, CHUNK_NUMBER, CLIENT_HOST, CLIENT_PORT
    config = configparser.ConfigParser()
    config.read('config.ini')
    SERVER_HOST = config['SERVER']['HOST']
    SERVER_PORT = int(config['SERVER']['PORT'])
    SERVER_BUFSIZ = int(config['SERVER']['BUFSIZ'])
    CHUNK_NUMBER = int(config['SERVER']['CHUNK_NUMBER'])
    CLIENT_HOST = config['CLIENT']['HOST']
    CLIENT_PORT = int(config['CLIENT']['PORT'])
    # print(SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ)
    return SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ, CHUNK_NUMBER, CLIENT_HOST, CLIENT_PORT