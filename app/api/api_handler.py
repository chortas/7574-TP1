import logging
import json
from threading import Thread
from queue import Queue

from sockets.socket import Socket
from socket import *
from block_builder import BlockBuilder
from stats.stats_reader import StatsReader
from common.utils import *

class ApiHandler():
    """Class that comunicates with the client and forwards the request to the corresponding
    entities"""

    def __init__(self, socket_port, listen_backlog, block_queue, query_host, query_port, 
    timeout_chunk, limit_chunk, n_clients, stats, graceful_stopper):
        self.socket = Socket()
        self.socket.bind_and_listen('', socket_port, listen_backlog)
        self.limit_chunk = limit_chunk
        self.chunk_queue = Queue()
        self.block_queue = block_queue
        self.block_builder = BlockBuilder(self.chunk_queue, self.block_queue, timeout_chunk)
        self.stats = stats
        self.query_host = query_host
        self.query_port = query_port
        self.runners = [Thread(target=self.run) for i in range(n_clients)]
        self.graceful_stopper = graceful_stopper

    def start(self):
        self.block_builder.start()
        for runner in self.runners:
            runner.start() 

    def run(self):
        while not self.graceful_stopper.has_been_stopped():
            client_socket = None
            try:
                client_socket = self.socket.accept_new_connection()
                self.__handle_client_connection(client_socket)
            except timeout:
                if self.graceful_stopper.has_been_stopped():    
                    self.__stop()
                    break
            except OSError as e:
                logging.info(f"[API_HANDLER] Error operating with socket: {e}")
            finally:
                if client_socket != None:
                    client_socket.close()
        logging.info("[API_HANDLER] End run")

    def __stop(self):
        empty_queue(self.chunk_queue)
        empty_queue(self.block_queue)
        self.block_builder.stop()
    
    def __handle_client_connection(self, client_socket):
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

        client_socket.send_data(response)

    def __handle_add_chunk(self, client_socket):
        chunk = client_socket.recv_data()
        if self.chunk_queue.qsize() == self.limit_chunk:
            return json.dumps({"status_code": 503, "message": "The system is overloaded at the moment. Try again later"})
        self.chunk_queue.put(chunk)
        return json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

    def __handle_get_query(self, client_socket, op):
        parameter_received = client_socket.recv_data()
        query_socket = Socket()
        try:
            query_socket.connect(self.query_host, self.query_port)

            query_socket.send_data(op)
            query_socket.recv_data() #ack
            query_socket.send_data(parameter_received)

            block = query_socket.recv_data()
            return json.dumps({"status_code": 200, "block": block})

        except OSError as e:
            logging.info(f"[API_HANDLER] Error operating with socket: {e}")

        finally:
            query_socket.close()
    
    def __handle_stats_query(self):
        stats = self.stats.read_stats()
        return json.dumps({"status_code": 200, "result": stats})

    def __handle_unknown_query(self):
        return json.dumps({"status_code": 404, "message": "Not Found"})