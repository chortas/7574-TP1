import socket
import json
from sockets.utils import *
from threading import Thread
from blockchain_reader import BlockchainReader
from queue import Queue

MAX_SIZE = 1024

class QueryManager:
    def __init__(self, socket_host, socket_port, listen_backlog, n_readers):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket_host, socket_port))
        self.socket.listen(listen_backlog)
        self.n_readers = n_readers
        self.request_queue = Queue()
        self.result_queue = Queue()
        self.blockchain_readers = [BlockchainReader(self.request_queue, self.result_queue) for _ in range(n_readers)]
        self.receiver_results = Thread(target=self.receive_results)

        self.start_threads()

    def start_threads(self):
        self.receiver_results.start()
        for i in range(self.n_readers):
            self.blockchain_readers[i].start()
    
    def receive_results(self):
        while True:
            result = self.result_queue.get()
            send_fixed_data(json.dumps(result["result"]), result["socket"])
                
    def receive_queries(self):
        while True:
            client_socket = accept_new_connection(self.socket)
            logging.info(f'[QUERY_MANAGER] Connected with {client_socket}')
            self.__handle_query_connection(client_socket)
    
    def __handle_query_connection(self, client_socket):
        """
        Read message from a specific miner socket and closes the socket
        If a problem arises in the communication with the client, the
        miner socket will also be closed
        """
        try:
            op = recv_fixed_data(client_socket, MAX_SIZE)
            logging.info(f'[QUERY_MANAGER] Operation received: {op}')

            send_fixed_data(json.dumps({"ack": True}), client_socket) #ack

            if op == "GET BLOCK":
                hash_received = recv_fixed_data(client_socket, MAX_SIZE)
                logging.info(f"[QUERY_MANAGER] Received hash: {hash_received}")
                self.request_queue.put({"operation": op, "hash": hash_received, "socket": client_socket})

            elif op == "GET BLOCKS BY MINUTE":
                pass
                '''timestamp_received = recv_fixed_data(client_socket, MAX_SIZE)
                logging.info(f"[QUERY_MANAGER] Received timestamp: {timestamp_received}")
                self.request_queue.put({"operation": op, "hash": hash_received, "socket": client_socket})
                '''

            else:
                result = json.dumps({"result": "FAILED"})

            #send_data(result, miner_socket)

        except OSError:
            logging.info("Error while reading socket {}".format(miner_socket))

