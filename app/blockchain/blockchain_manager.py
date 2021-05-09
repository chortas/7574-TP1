import socket
import json
from common.block import Block
from common.cryptographic_solver import CryptographicSolver
from blockchain_writer import BlockchainWriter
from sockets.utils import *

class BlockchainManager:
    def __init__(self, socket_host, socket_port):
        self.blocks = []
        self.last_block_hash = 0
        self.cryptographic_solver = CryptographicSolver()
        self.blockchain_writer = BlockchainWriter()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket_host, socket_port))
        self.socket.listen(1)

    def receive_blocks(self):
        #TODO: this should be a while true loop

        while True:
            print('[BLOCKCHAIN_MANAGER] Socket now listening')
            miner_socket = accept_new_connection(self.socket)
            print(f'[BLOCKCHAIN_MANAGER] Connected with {miner_socket}')
            self.__handle_miner_connection(miner_socket)

    def __handle_miner_connection(self, miner_socket):
        """
        Read message from a specific miner socket and closes the socket
        If a problem arises in the communication with the client, the
        miner socket will also be closed
        """
        try:
            block_serialized = recv_data(miner_socket)
            print(f'Block serialized: {block_serialized} - type: {type(block_serialized)}')
            block = Block.deserialize(block_serialized)
            result = {}
            if self.add_block(block):
                result = json.dumps({"hash": block.hash(), "result": "OK"})
            else:
                result = json.dumps({"result": "FAILED"})
            send_data(result, miner_socket)

        except OSError:
            logging.info("Error while reading socket {}".format(miner_socket))
        finally:
            miner_socket.close()

    def add_block(self, new_block):
        if (self.is_block_valid(new_block)):
            self.blocks.append(new_block)
            self.last_block_hash = new_block.hash()
            self.blockchain_writer.write_block(new_block) #TODO: see if this could be in a different thread
            return True
        return False
    
    def is_block_valid(self, block):
        return block.get_prev_hash() == self.last_block_hash and self.cryptographic_solver.solve(block)
    
    def get_last_hash(self):
        return self.last_block_hash
    