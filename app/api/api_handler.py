import logging
import json
from threading import Thread
from queue import Queue

from sockets.socket import Socket
from block_builder import BlockBuilder
from stats.stats_reader import StatsReader
from common.utils import *

class ApiHandler():
    """Class that comunicates with the client and forwards the request to the corresponding
    entities"""

    def __init__(self, socket_port, listen_backlog, miner_manager, query_host, query_port, 
    timeout_chunk, limit_chunk, n_clients, stats):
        self.socket = Socket()
        self.socket.bind_and_listen('', socket_port, listen_backlog)
        self.miner_manager = miner_manager
        self.limit_chunk = limit_chunk
        self.chunk_queue = Queue()
        self.block_queue = miner_manager.get_block_queue()
        self.block_builder = BlockBuilder(self.chunk_queue, self.block_queue, timeout_chunk)
        self.stats = stats
        self.query_host = query_host
        self.query_port = query_port
        self.runners = [Thread(target=self.run) for i in range(n_clients)]

    def start_readers(self):
        self.block_builder.start()
        self.miner_manager.start()
        for runner in self.runners:
            runner.start()

    def run(self):
        while True:
            try:
                client_socket = self.socket.accept_new_connection()
                self.__handle_client_connection(client_socket)
            except OSError:
                logging.info("[API_HANDLER] Socket timeout")
    
    def __handle_client_connection(self, client_socket):
        try:
            op = client_socket.recv_data()
            client_socket.send_data(json.dumps({"ack": True})) #ack

            response = None

            if op == ADD_CHUNK_CODE_OP:
                response = self.__handle_add_chunk(client_socket)
                
            elif op == GET_BLOCK_BY_HASH_OP or op == GET_BLOCKS_BY_TIMESTAMP_OP:
                response = self.__handle_get_query(client_socket, op)            

            elif op == GET_STATS_OP:
                response = self.__handle_stats_query()

            else:
                response = self.__handle_unknown_query()

            logging.info(f"[API_HANDLER] Sending response to client: {response}")
            client_socket.send_data(response)
        
        except OSError:
            logging.info(f"[API_HANDLER] Error while reading socket {client_socket}")

        finally:
            client_socket.close()

    def __handle_add_chunk(self, client_socket):
        chunk = client_socket.recv_data()
        if self.chunk_queue.qsize() == self.limit_chunk:
            return json.dumps({"status_code": 503, "message": "The system is overloaded at the moment. Try again later"})
        self.chunk_queue.put(chunk)
        return json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

    def __handle_get_query(self, client_socket, op):
        parameter_received = client_socket.recv_data()
        logging.info(f"[API_HANDLER] Parameter received: {parameter_received}")

        query_socket = Socket()
        query_socket.connect(self.query_host, self.query_port)

        query_socket.send_data(op)
        query_socket.recv_data() #ack
        query_socket.send_data(parameter_received)

        block = query_socket.recv_data()

        query_socket.close()

        return json.dumps({"status_code": 200, "block": block})
    
    def __handle_stats_query(self):
        stats = self.stats.read_stats()
        return json.dumps({"status_code": 200, "result": stats})

    def __handle_unknown_query(self):
        return json.dumps({"status_code": 404, "message": "Not Found"})