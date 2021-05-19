import socket
import logging
from common.utils import *

NUM_PARAM_BYTES = 4

class Socket:
    def __init__(self, socket_built=None):
        if socket_built:
            self.socket = socket_built
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.socket.connect((host, port))

    def bind_and_listen(self, host, port, n_listeners):
        self.socket.bind((host, port))
        self.socket.listen(n_listeners)

    def accept_new_connection(self):
        conn, addr = self.socket.accept()
        logging.info('Got connection from {}'.format(addr))
        return Socket(conn)

    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.socket.close() 

    def send_data(self, data):
        self.socket.sendall(number_to_4_bytes(len(data)))
        self.socket.sendall(data.encode())

    def recv_data(self):
        data_len = bytes_4_to_number(self.socket.recv(NUM_PARAM_BYTES))
        return self.socket.recv(data_len).rstrip().decode()
