import socket
import json
from sockets.utils import *
from block_builder import BlockBuilder

MAX_CHUNK_SIZE = 65536
MAX_OP = 1024

class ApiHandler:
    def __init__(self, socket_port, listen_backlog, miner_manager):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', socket_port))
        self.socket.listen(listen_backlog)
        self.block_builder = BlockBuilder()
        self.miner_manager = miner_manager

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
            op = recv_fixed_data(client_sock, MAX_OP)
            logging.info(f"Operation received: {op}")
            response = None

            if op == "ADD CHUNK":
                chunk = recv_fixed_data(client_sock, MAX_CHUNK_SIZE)
                block = self.block_builder.add_chunk(chunk)
                if block != None: # to keep receiving chunks
                    self.miner_manager.send_block(block)
                response = json.dumps({"status_code": 200, "message": "The chunk will be processed shortly"})  

            elif op == "GET BLOCK":
                # TODO: do this
                response = json.dumps({"status_code": 200, "block": {}})
            
            elif op == "GET BLOCKS BY MINUTE":
                # TODO: do this
                response = json.dumps({"status_code": 200, "blocks": []})

            elif op == "GET STATS":
                response = json.dumps({"status_code": 200, "result": {}})
            
            else:
                response = json.dumps({"status_code": 404, "message": "Not Found"})

            send_fixed_data(response, client_sock)
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
            client_sock.close()
