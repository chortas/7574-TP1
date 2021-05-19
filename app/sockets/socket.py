import socket
import logging

NUM_PARAM_BYTES = 4
MAX_CHUNK_SIZE = 65536
MAX_SIZE = 1024
MAX_BLOCK_LEN = 16777216

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

    def send_fixed_data(self, data):
        self.socket.send(data.encode())

    def recv_fixed_data(self, data_len):
        return self.socket.recv(data_len).rstrip().decode()    
