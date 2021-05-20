import socket
import json
import logging
from time import sleep
from common.block import Block
from common.cryptographic_solver import CryptographicSolver
from blockchain_writer import BlockchainWriter
from threading import Thread
from sockets.socket import Socket

class BlockchainManager(Thread):
    """Class that receives the bloks procesed by the miners and adds them to the blockchain
    if corresponds""" 

    def __init__(self, socket_host, socket_port, listen_backlog):
        Thread.__init__(self)
        self.last_block_hash = 0
        self.cryptographic_solver = CryptographicSolver()
        self.blockchain_writer = BlockchainWriter()
        self.socket = Socket()
        self.socket.bind_and_listen(socket_host, socket_port, listen_backlog)

    def run(self):
        while True:
            miner_socket = self.socket.accept_new_connection()
            self.__handle_miner_connection(miner_socket)

    def __handle_miner_connection(self, miner_socket):
        try:
            block_serialized = miner_socket.recv_data()
            block = Block.deserialize(block_serialized)
            result = {}
            if self.__add_block(block):
                sleep(3)
                logging.info(f"[BLOCKCHAIN_MANAGER] Block added: {block}")
                result = json.dumps({"hash": block.hash(), "result": "OK"})
            else:
                result = json.dumps({"result": "FAILED"})
            miner_socket.send_data(result)

        except OSError:
            logging.info(f"[BLOCKCHAIN_MANAGER] Error while reading socket {miner_socket}")
        finally:
            miner_socket.close()

    def __add_block(self, new_block):
        if (self.__is_block_valid(new_block)):
            self.last_block_hash = new_block.hash()
            self.blockchain_writer.write_block(new_block)
            return True
        return False
    
    def __is_block_valid(self, block):
        return block.get_prev_hash() == self.last_block_hash and self.cryptographic_solver.solve(block, block.get_hash())
    