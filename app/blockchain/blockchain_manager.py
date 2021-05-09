import socket
from common.block import Block
from common.cryptographic_solver import CryptographicSolver
from sockets.utils import *

class BlockchainManager:
    def __init__(self, socket_host, socket_port):
        self.blocks = []
        self.last_block_hash = 0
        self.cryptographic_solver = CryptographicSolver()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket_host, socket_port))
        self.socket.listen(1)

    def receive_blocks(self):
        #TODO: this should be a while true loop

        print('[BLOCKCHAIN_MANAGER] Socket now listening')

        miner_socket = accept_new_connection(self.socket)
        print(f'[BLOCKCHAIN_MANAGER] Connected with {miner_socket}')
        self.__handle_miner_connection(miner_socket)

        second_miner_socket = accept_new_connection(self.socket)
        print(f'[BLOCKCHAIN_MANAGER] Connected with {second_miner_socket}')
        self.__handle_miner_connection(second_miner_socket)

    def __handle_miner_connection(self, miner_socket):
        """
        Read message from a specific miner socket and closes the socket
        If a problem arises in the communication with the client, the
        miner socket will also be closed
        """
        try:
            block_len = bytes_4_to_number(miner_socket.recv(NUM_PARAM_BYTES))
            print(f'Block len: {block_len}')
            block_serialized = miner_socket.recv(block_len).decode()
            print(f'Block serialized: {block_serialized} - type: {type(block_serialized)}')
            block = Block.deserialize(block_serialized)
            print(f"Block: {block}")

        except OSError:
            logging.info("Error while reading socket {}".format(miner_socket))
        finally:
            miner_socket.close()

    def add_block(self, newBlock):
        # add communication with miner
        
        if (self.isBlockValid(newBlock)):
            self.blocks.append(newBlock)
            self.last_block_hash = newBlock.hash()
            return True
        return False
    
    def is_block_valid(self, block):
        return block.header.get_prev_hash() == self.last_block_hash and self.cryptographic_solver.solve(block)
    
    def get_last_hash(self):
        return self.last_block_hash
    