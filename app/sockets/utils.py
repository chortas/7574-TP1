import socket

NUM_PARAM_BYTES = 4

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

    print("Proceed to accept new connections")
    conn, addr = socket.accept()
    print('Got connection from {}'.format(addr))
    return conn

def close(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except:
        pass
    sock.close()

def number_to_4_bytes(num):
    result = bytearray()
    for i in range(4):
        result.append(num & 255)
        num = num >> 8
    return result

def bytes_4_to_number(b):
    res = 0
    for i in range(4):
        res += b[i] << (i*8)
    return res
