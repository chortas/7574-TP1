import json
import logging
from threading import Thread
from queue import Queue, Empty
from socket import *

from sockets.socket import Socket
from blockchain_reader import BlockchainReader
from common.utils import *

class QueryManager(Thread):
    """Class that handles the querys and forwards them to the blockchain readers"""

    def __init__(self, socket_host, socket_port, listen_backlog, n_readers, block_index_lock, 
    block_lock, graceful_stopper):
        Thread.__init__(self)
        self.socket = Socket()
        self.socket.bind_and_listen(socket_host, socket_port, listen_backlog)
        self.n_readers = n_readers
        self.request_queue = Queue()
        self.result_queue = Queue()
        self.blockchain_readers = [BlockchainReader(self.request_queue, self.result_queue, block_index_lock, block_lock) for _ in range(n_readers)]
        self.receiver_results = Thread(target=self.__receive_results)
        self.graceful_stopper = graceful_stopper
                
    def run(self):
        self.__start_threads()
        while not self.graceful_stopper.has_been_stopped():
            client_socket = None
            try:
                client_socket = self.socket.accept_new_connection()
                self.__handle_query_connection(client_socket)
            except timeout:
                if self.graceful_stopper.has_been_stopped():
                    self.__stop()
            except OSError as e:
                logging.info(f"[QUERY_MANAGER] Error while operating with sockets: {e}")
        logging.info("[QUERY_MANAGER] End run")
            
    def __start_threads(self):
        self.receiver_results.start()
        for i in range(self.n_readers):
            self.blockchain_readers[i].start()
    
    def __receive_results(self):
        while not self.graceful_stopper.has_been_stopped():
            client_socket = None
            try:
                result = self.result_queue.get(timeout=OPERATION_TIMEOUT)
                client_socket = result["socket"]
                client_socket.send_data(json.dumps(result["result"]))
            except (Empty, timeout):
                if self.graceful_stopper.has_been_stopped():
                    self.__stop()
            except OSError as e:
                logging.info(f"[QUERY_MANAGER] Error while operating with sockets: {e}")
            finally:
                if client_socket != None:
                    client_socket.close()

    def __stop(self):
        empty_queue(self.request_queue)
        empty_queue(self.result_queue)
        for i in range(self.n_readers):
            self.blockchain_readers[i].stop()

    def __handle_query_connection(self, client_socket):
        op = client_socket.recv_data()

        client_socket.send_data(json.dumps({"ack": True})) #ack

        if op == GET_BLOCK_BY_HASH_OP:
            hash_received = client_socket.recv_data()
            self.request_queue.put({"operation": op, "hash": hash_received, "socket": client_socket})

        elif op == GET_BLOCKS_BY_TIMESTAMP_OP:
            timestamp_received = client_socket.recv_data()
            self.request_queue.put({"operation": op, "timestamp": timestamp_received, "socket": client_socket})
