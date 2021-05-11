import socket
import logging

NUM_PARAM_BYTES = 4
MAX_CHUNK_SIZE = 65536
MAX_SIZE = 1024
MAX_BLOCK_LEN = 16777216

def create_and_connect(host, port):
    socket_created = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_created.connect((host, port))
    return socket_created

def accept_new_connection(socket):
    """
    Accept new connections
    Function blocks until a connection to a client is made.
    Then connection created is printed and returned
    """

    logging.info("Proceed to accept new connections")
    conn, addr = socket.accept()
    logging.info('Got connection from {}'.format(addr))
    return conn

def close(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except:
        pass
    sock.close()

def send_fixed_data(data, socket):
    socket.send(data.encode())

def recv_fixed_data(socket, data_len):
    return socket.recv(data_len).rstrip().decode()    
