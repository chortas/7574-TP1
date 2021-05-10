import socket
import json
from sockets.utils import *
from block_builder import BlockBuilder
from stats.stats_reader import StatsReader
from queue import Queue

MAX_CHUNK_SIZE = 65536
MAX_SIZE = 1024
BLOCK_LEN = 16777216

class ApiHandler:
    def __init__(self, socket_port, listen_backlog, miner_manager, query_host, query_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', socket_port))
        self.socket.listen(listen_backlog)

        self.miner_manager = miner_manager

        self.chunk_queue = Queue()
        self.block_queue = miner_manager.get_block_queue()
        self.block_builder = BlockBuilder(self.chunk_queue, self.block_queue)

        self.stats_reader_queue = Queue()
        self.stats_reader_result_queue = Queue()
        self.stats_reader = StatsReader(self.stats_reader_queue, self.stats_reader_result_queue)

        self.query_host = query_host
        self.query_port = query_port

        self.start_readers()

    def start_readers(self):
        self.stats_reader.start()
        self.block_builder.start()
        self.miner_manager.start()

    def run(self):
        while True:
            client_sock = accept_new_connection(self.socket)
            if not client_sock:
                break
            self.__handle_client_connection(client_sock)
    
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            op = recv_fixed_data(client_sock, MAX_SIZE)
            logging.info(f"Operation received: {op}")
            response = None

            if op == "ADD CHUNK":
                chunk = recv_fixed_data(client_sock, MAX_CHUNK_SIZE)
                self.chunk_queue.put(chunk)
                response = json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

            elif op == "GET BLOCK":
                hash_received = recv_fixed_data(client_sock, MAX_SIZE)

                query_socket = create_and_connect(self.query_host, self.query_port)

                send_fixed_data(op, query_socket)
                recv_fixed_data(query_socket, MAX_SIZE)
                send_fixed_data(hash_received, query_socket)

                block = recv_fixed_data(query_socket, BLOCK_LEN)

                close(query_socket)

                response = json.dumps({"status_code": 200, "block": block})
            
            elif op == "GET BLOCKS BY MINUTE":
                timestamp_received = recv_fixed_data(client_sock, MAX_SIZE)

                query_socket = create_and_connect(self.query_host, self.query_port)

                send_fixed_data(op, query_socket)
                recv_fixed_data(query_socket, MAX_SIZE)
                send_fixed_data(timestamp_received, query_socket)

                blocks = recv_fixed_data(query_socket, BLOCK_LEN)

                close(query_socket)

                response = json.dumps({"status_code": 200, "blocks": blocks})

            elif op == "GET STATS":
                self.stats_reader_queue.put(True)
                stats = self.stats_reader_result_queue.get()
                response = json.dumps({"status_code": 200, "result": stats})

            else:
                response = json.dumps({"status_code": 404, "message": "Not Found"})

            send_fixed_data(response, client_sock)
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
            client_sock.close()
