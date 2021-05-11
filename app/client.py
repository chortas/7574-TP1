import socket
import logging
from time import sleep
from sockets.utils import *

API_PORT = 8080 
API_HOST = "127.0.0.1"

def main():
    
    # Test 1 -> Guardar 256 chunks consiste en guardar 1 bloque
    # test_add_chunks_until_limit()

    # Test 2 -> Si hay <256 chunks, después de cierto timeout configurable se manda
    # test_chunk_is_sent_if_timeout()

    # Test 3 -> Si se manda más de 256 chunks se envian en bloques distintos
    # test_add_chunks_past_limit()

    # Test 4 -> Si se pide un bloque con un hash desconocido devuelve vacio
    # test_get_block_by_unknown_hash()

    # Test 5 -> Si se pide un bloque con un hash conocido <reemplazar en demo> devuelve el correspondiente
    # test_get_block_by_known_hash("94872455518301211611174060337313215717928923152270874949483639728561342568220")
    
    # Test 6 -> Si se pide un bloque con un timestamp desconocido devuelve vacio
    # test_get_blocks_by_unknown_timestamp()

    # Test 7 -> Si se pide un bloque con un timestamp conocido <reemplazar en demo> devuelve el correspondiente
    # test_get_blocks_by_known_timestamp("2021-05-11 21:57")

    # Test 8 -> Si se piden las stats se dan las correctas
    # test_get_stats()

    # Test 9 -> Si se agregan más de 256 bloques se ajusta la dificultad
    # test_difficulty()

def test_add_chunks_until_limit():
    for i in range(256):
        client_socket = create_and_connect(API_HOST, API_PORT)
        result = add_chunk(client_socket, str(i))
        close(client_socket)

def test_chunk_is_sent_if_timeout():
    client_socket = create_and_connect(API_HOST, API_PORT)
    add_chunk(client_socket, "1")
    sleep(15) # timeout is 15
    close(client_socket)

def test_add_chunks_past_limit():
    for i in range(256*2):
        client_socket = create_and_connect(API_HOST, API_PORT)
        result = add_chunk(client_socket, str(i))
        close(client_socket)

def test_get_block_by_unknown_hash():
    client_socket = create_and_connect(API_HOST, API_PORT)
    result = get_chunk(client_socket, "0")
    print(result)

def test_get_block_by_known_hash(hash_value):
    client_socket = create_and_connect(API_HOST, API_PORT)
    result = get_chunk(client_socket, hash_value)
    print(result)

def test_get_blocks_by_unknown_timestamp():
    client_socket = create_and_connect(API_HOST, API_PORT)
    result = get_chunks_by_minute(client_socket, "2021-02-11 22:00")
    print(result)

def test_get_blocks_by_known_timestamp(timestamp):
    client_socket = create_and_connect(API_HOST, API_PORT)
    result = get_chunks_by_minute(client_socket, timestamp)
    print(result)

def test_get_stats():
    client_socket = create_and_connect(API_HOST, API_PORT)
    result = get_stats(client_socket)
    print(result)

def test_difficulty():
    client_socket = create_and_connect(API_HOST, API_PORT)
    for i in range(257):
        test_add_chunks_until_limit()

def get_stats(client_socket):
    operation = "GET STATS"
    send_fixed_data(operation, client_socket)
    recv_fixed_data(client_socket, MAX_SIZE) #ack
    return recv_fixed_data(client_socket, MAX_BLOCK_LEN)

def get_chunks_by_minute(client_socket, timestamp):
    operation = "GET BLOCKS BY MINUTE"
    send_fixed_data(operation, client_socket)
    recv_fixed_data(client_socket, MAX_SIZE) #ack
    send_fixed_data(timestamp, client_socket)
    return recv_fixed_data(client_socket, MAX_BLOCK_LEN)

def get_chunk(client_socket, hash_value):
    operation = "GET BLOCK"
    send_fixed_data(operation, client_socket)
    recv_fixed_data(client_socket, MAX_SIZE) #ack
    send_fixed_data(hash_value, client_socket)
    return recv_fixed_data(client_socket, MAX_BLOCK_LEN)

def add_chunk(client_socket, chunk):
    operation = "ADD CHUNK"
    send_fixed_data(operation, client_socket)
    recv_fixed_data(client_socket, MAX_SIZE) #ack
    send_fixed_data(chunk, client_socket)
    return recv_fixed_data(client_socket, MAX_BLOCK_LEN)
  
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