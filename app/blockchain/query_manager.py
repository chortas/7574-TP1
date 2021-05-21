import json
import logging
from threading import Thread
from queue import Queue

from sockets.socket import Socket
from blockchain_reader import BlockchainReader
from common.utils import *

class QueryManager:
    """Class that handles the querys and forwards them to the blockchain readers"""

    def __init__(self, socket_host, socket_port, listen_backlog, n_readers):
        self.socket = Socket()
        self.socket.bind_and_listen(socket_host, socket_port, listen_backlog)
        self.n_readers = n_readers
        self.request_queue = Queue()
        self.result_queue = Queue()
        self.blockchain_readers = [BlockchainReader(self.request_queue, self.result_queue) for _ in range(n_readers)]
        self.receiver_results = Thread(target=self.__receive_results)

        self.__start_threads()
                
    def receive_queries(self):
        while True:
            client_socket = self.socket.accept_new_connection()
            self.__handle_query_connection(client_socket)

    def __start_threads(self):
        self.receiver_results.start()
        for i in range(self.n_readers):
            self.blockchain_readers[i].start()
    
    def __receive_results(self):
        while True:
            result = self.result_queue.get()
            client_socket = result["socket"]
            client_socket.send_data(json.dumps(result["result"]))
            client_socket.close()   
            
    def __handle_query_connection(self, client_socket):
        """
        Read message from a specific miner socket and closes the socket
        If a problem arises in the communication with the client, the
        miner socket will also be closed
        """
        try:
            op = client_socket.recv_data()

            client_socket.send_data(json.dumps({"ack": True})) #ack

            if op == GET_BLOCK_BY_HASH_OP:
                hash_received = client_socket.recv_data()
                self.request_queue.put({"operation": op, "hash": hash_received, "socket": client_socket})

            elif op == GET_BLOCKS_BY_TIMESTAMP_OP:
                timestamp_received = client_socket.recv_data()
                self.request_queue.put({"operation": op, "timestamp": timestamp_received, "socket": client_socket})

        except OSError:
            logging.info(f"[QUERY_MANAGER] Error while reading socket {client_socket}")
