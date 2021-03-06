import socket
import logging
from time import sleep
from threading import Thread
from sockets.socket import Socket
from common.utils import *

API_PORT = 8080 
API_HOST = "127.0.0.1"

def main():
    
    # Test 1 -> Guardar 256 chunks consiste en guardar 1 bloque
    test_add_chunks_until_limit()

    # Test 2 -> Si hay <256 chunks, después de cierto timeout configurable se manda
    # test_chunk_is_sent_if_timeout()

    # Test 3 -> Si se manda más de 256 chunks se envian en bloques distintos
    # test_add_chunks_past_limit()

    # Test 4 -> Si se pide un bloque con un hash desconocido devuelve vacio
    test_get_block_by_unknown_hash()

    # Test 5 -> Si se pide un bloque con un hash conocido <reemplazar en demo> devuelve el correspondiente
    test_get_block_by_known_hash("2877771413925750486914068401421537597022408690473403355243978210213298972505")
    
    # Test 6 -> Si se pide un bloque con un timestamp desconocido devuelve vacio
    # test_get_blocks_by_unknown_timestamp()

    # Test 7 -> Si se pide un bloque con un timestamp conocido <reemplazar en demo> devuelve el correspondiente
    test_get_blocks_by_known_timestamp("2021-05-24 16:32")

    # Test 8 -> Si se piden las stats se dan las correctas
    test_get_stats()

    # Test 9 -> Si se agregan más de 256 bloques se ajusta la dificultad
    test_difficulty()

    # Test 10 -> Abro más clientes
    # test_many_clients()

def test_many_clients():
    for i in range(10):
        client_socket = Socket()
        client_socket.connect(API_HOST, API_PORT)
        client = Thread(target=add_chunk, args=(client_socket,str(i)))
        client.start()

def test_add_chunks_until_limit():
    for i in range(256):
        client_socket = Socket()
        client_socket.connect(API_HOST, API_PORT)
        result = add_chunk(client_socket, str(i))
        client_socket.close()

def test_chunk_is_sent_if_timeout():
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    add_chunk(client_socket, "1")
    sleep(15) # timeout is 15
    client_socket.close()

def test_add_chunks_past_limit():
    for i in range(256*2):
        client_socket = Socket()
        client_socket.connect(API_HOST, API_PORT)
        result = add_chunk(client_socket, str(i))
        client_socket.close()

def test_get_block_by_unknown_hash():
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    result = get_chunk(client_socket, "0")
    print(result)

def test_get_block_by_known_hash(hash_value):
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    result = get_chunk(client_socket, hash_value)
    print(result)

def test_get_blocks_by_unknown_timestamp():
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    result = get_chunks_by_minute(client_socket, "2021-02-11 22:00")
    print(result)

def test_get_blocks_by_known_timestamp(timestamp):
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    result = get_chunks_by_minute(client_socket, timestamp)
    print(result)

def test_get_stats():
    client_socket = Socket()
    client_socket.connect(API_HOST, API_PORT)
    result = get_stats(client_socket)
    print(result)

def test_difficulty():
    for i in range(257):
        print(f"Sending a block attempt {i}")
        test_add_chunks_until_limit()

def get_stats(client_socket):
    operation = GET_STATS_OP
    client_socket.send_data(operation)
    client_socket.recv_data() #ack
    return client_socket.recv_data()

def get_chunks_by_minute(client_socket, timestamp):
    operation = GET_BLOCKS_BY_TIMESTAMP_OP
    client_socket.send_data(operation)
    client_socket.recv_data() #ack
    client_socket.send_data(timestamp)
    return client_socket.recv_data()

def get_chunk(client_socket, hash_value):
    operation = GET_BLOCK_BY_HASH_OP
    client_socket.send_data(operation)
    client_socket.recv_data() #ack
    client_socket.send_data(hash_value)
    return client_socket.recv_data()

def add_chunk(client_socket, chunk):
    operation = ADD_CHUNK_CODE_OP
    client_socket.send_data(operation)
    client_socket.recv_data() #ack
    client_socket.send_data(chunk)
    return client_socket.recv_data()
  
def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__== "__main__":
    main()