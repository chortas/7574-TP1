import socket
import logging
import json
from threading import Thread
from sockets.socket import Socket
from block_builder import BlockBuilder
from stats.stats_reader import StatsReader
from queue import Queue

class ApiHandler:
    """Class that comunicates with the client and forwards the request to the corresponding
    entities"""

    def __init__(self, socket_port, listen_backlog, miner_manager, query_host, query_port, 
    timeout_chunk, limit_chunk, n_clients):
        self.socket = Socket()
        self.socket.bind_and_listen('', socket_port, listen_backlog)

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
            client_socket = self.socket.accept_new_connection()
            if not client_socket:
                break
            self.__handle_client_connection(client_socket)
    
    def __handle_client_connection(self, client_socket):
        try:
            op = client_socket.recv_data()
            logging.info(f"[API_HANDLER] Operation received: {op}")
            client_socket.send_data(json.dumps({"ack": True})) #ack

            response = None

            if op == "POST":
                chunk = client_socket.recv_data()
                if self.chunk_queue.qsize() == self.limit_chunk:
                    response = json.dumps({"status_code": 503, "message": "The system is overloaded at the moment. Try again later"})
                else:
                    self.chunk_queue.put(chunk)
                    response = json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

            elif op == "GETH":
                hash_received = client_socket.recv_data()
                logging.info(f"[API_HANDLER] Hash received: {hash_received}")

                query_socket = Socket()
                query_socket.connect(self.query_host, self.query_port)

                query_socket.send_data(op)
                logging.info(f"[API_HANDLER] Sent operation")
                query_socket.recv_data()
                logging.info(f"[API_HANDLER] Recv ack")
                query_socket.send_data(hash_received)
                logging.info(f"[API_HANDLER] Sent hash")

                block = query_socket.recv_data()
                logging.info(f"[API_HANDLER] Received block")

                query_socket.close()

                response = json.dumps({"status_code": 200, "block": block})
            
            elif op == "GETT":
                timestamp_received = client_socket.recv_data()
                logging.info(f"[API_HANDLER] Timestamp received: {timestamp_received}")

                query_socket = Socket()
                query_socket.connect(self.query_host, self.query_port)
                
                query_socket.send_data(op)
                query_socket.recv_data()
                query_socket.send_data(timestamp_received)

                blocks = query_socket.recv_data()

                query_socket.close()

                response = json.dumps({"status_code": 200, "blocks": blocks})

            elif op == "STAT":
                self.stats_reader_queue.put(True)
                stats = self.stats_reader_result_queue.get()
                response = json.dumps({"status_code": 200, "result": stats})

            else:
                response = json.dumps({"status_code": 404, "message": "Not Found"})

            logging.info(f"[API_HANDLER] Sending response to client: {response}")
            client_socket.send_data(response)
        except OSError:
            logging.info(f"[API_HANDLER] Error while reading socket {client_socket}")
        finally:
            client_socket.close()
