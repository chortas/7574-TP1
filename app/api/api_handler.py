import socket
import logging
import json
from threading import Thread
from sockets.utils import *
from block_builder import BlockBuilder
from stats.stats_reader import StatsReader
from queue import Queue

class ApiHandler:
    """Class that comunicates with the client and forwards the request to the corresponding
    entities"""

    def __init__(self, socket_port, listen_backlog, miner_manager, query_host, query_port, 
    timeout_chunk, limit_chunk, n_clients):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', socket_port))
        self.socket.listen(listen_backlog)

        self.miner_manager = miner_manager

        self.limit_chunk = limit_chunk
        self.chunk_queue = Queue()
        self.block_queue = miner_manager.get_block_queue()
        self.block_builder = BlockBuilder(self.chunk_queue, self.block_queue, timeout_chunk)

        self.stats_reader_queue = Queue()
        self.stats_reader_result_queue = Queue()
        self.stats_reader = StatsReader(self.stats_reader_queue, self.stats_reader_result_queue)

        self.query_host = query_host
        self.query_port = query_port

        self.runners = [Thread(target=self.run) for i in range(n_clients)]

    def start_readers(self):
        self.stats_reader.start()
        self.block_builder.start()
        self.miner_manager.start()
        for runner in self.runners:
            runner.start()

    def run(self):
        while True:
            client_sock = accept_new_connection(self.socket)
            if not client_sock:
                break
            self.__handle_client_connection(client_sock)
    
    def __handle_client_connection(self, client_sock):
        try:
            op = recv_fixed_data(client_sock, MAX_SIZE)
            logging.info(f"[API_HANDLER] Operation received: {op}")
            send_fixed_data(json.dumps({"ack": True}), client_sock) #ack

            response = None

            if op == "ADD CHUNK":
                chunk = recv_fixed_data(client_sock, MAX_CHUNK_SIZE)
                if self.chunk_queue.qsize() == self.limit_chunk:
                    response = json.dumps({"status_code": 503, "message": "The system is overloaded at the moment. Try again later"})
                else:
                    self.chunk_queue.put(chunk)
                    response = json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

            elif op == "GET BLOCK":
                hash_received = recv_fixed_data(client_sock, MAX_SIZE)
                logging.info(f"[API_HANDLER] Hash received: {hash_received}")

                query_socket = create_and_connect(self.query_host, self.query_port)

                send_fixed_data(op, query_socket)
                recv_fixed_data(query_socket, MAX_SIZE)
                send_fixed_data(hash_received, query_socket)

                block = recv_fixed_data(query_socket, MAX_BLOCK_LEN)

                close(query_socket)

                response = json.dumps({"status_code": 200, "block": block})
            
            elif op == "GET BLOCKS BY MINUTE":
                timestamp_received = recv_fixed_data(client_sock, MAX_SIZE)
                logging.info(f"[API_HANDLER] Timestamp received: {timestamp_received}")

                query_socket = create_and_connect(self.query_host, self.query_port)

                send_fixed_data(op, query_socket)
                recv_fixed_data(query_socket, MAX_SIZE)
                send_fixed_data(timestamp_received, query_socket)

                blocks = recv_fixed_data(query_socket, MAX_BLOCK_LEN)

                close(query_socket)

                response = json.dumps({"status_code": 200, "blocks": blocks})

            elif op == "GET STATS":
                self.stats_reader_queue.put(True)
                stats = self.stats_reader_result_queue.get()
                response = json.dumps({"status_code": 200, "result": stats})

            else:
                response = json.dumps({"status_code": 404, "message": "Not Found"})

            logging.info(f"[API_HANDLER] Sending response to client: {response}")
            send_fixed_data(response, client_sock)
        except OSError:
            logging.info(f"[API_HANDLER] Error while reading socket {client_sock}")
        finally:
            client_sock.close()
