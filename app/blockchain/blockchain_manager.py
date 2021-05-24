import json
import logging
from threading import Thread

from common.block import Block
from common.cryptographic_solver import CryptographicSolver
from sockets.socket import Socket

class BlockchainManager(Thread):
    """Class that receives the bloks procesed by the miners and adds them to the blockchain
    if corresponds""" 

    def __init__(self, socket_host, socket_port, listen_backlog, blockchain_writer, graceful_stopper):
        Thread.__init__(self)
        self.last_block_hash = 0
        self.cryptographic_solver = CryptographicSolver()
        self.blockchain_writer = blockchain_writer
        self.socket = Socket()
        self.socket.bind_and_listen(socket_host, socket_port, listen_backlog)
        self.graceful_stopper = graceful_stopper

    def run(self):
        while not self.graceful_stopper.has_been_stopped():
            try:
                miner_socket = self.socket.accept_new_connection()
                self.__handle_miner_connection(miner_socket)
            except OSError:
                self.graceful_stopper.exit_gracefully()
        logging.info("[BLOCKCHAIN_MANAGER] End run")

    def __handle_miner_connection(self, miner_socket):
        try:
            block_serialized = miner_socket.recv_data()
            block = Block.deserialize(block_serialized)
            result = {}
            if self.__add_block(block):
                logging.info(f"[BLOCKCHAIN_MANAGER] Block added: {block}")
                result = json.dumps({"hash": block.compute_hash(), "result": "OK"})
            else:
                result = json.dumps({"result": "FAILED"})
            miner_socket.send_data(result)

        except OSError:
            logging.info(f"[BLOCKCHAIN_MANAGER] Error while reading socket")
            self.graceful_stopper.exit_gracefully()

        finally:
            miner_socket.close()

    def __add_block(self, new_block):
        if (self.__is_block_valid(new_block)):
            self.last_block_hash = new_block.compute_hash()
            self.blockchain_writer.write_block(new_block)
            return True
        return False
    
    def __is_block_valid(self, block):
        return block.prev_hash == self.last_block_hash and self.cryptographic_solver.solve(block, block.compute_hash())
    