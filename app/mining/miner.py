from threading import Thread
import json
import logging

from common.cryptographic_solver import CryptographicSolver
from sockets.socket import Socket
from common.utils import *

class Miner(Thread):
    """Class that mines a block"""

    def __init__(self, block_queue, stop_queue, result_queue, miner_id, 
    blockchain_host, blockchain_port, prev_hash_queue, stats_writer, ack_stop_queue):
        Thread.__init__(self)
        self.cryptographic_solver = CryptographicSolver()
        self.block_queue = block_queue
        self.stop_queue = stop_queue
        self.result_queue = result_queue
        self.id = miner_id
        self.blockchain_host = blockchain_host
        self.blockchain_port = blockchain_port
        self.prev_hash_queue = prev_hash_queue
        self.stats_writer = stats_writer
        self.ack_stop_queue = ack_stop_queue

    def mine(self, block):
        block.set_timestamp(get_and_format_datetime_now())
        while not self.cryptographic_solver.solve(block, block.hash()) and self.stop_queue.empty():
            block.add_nonce()
            block.set_timestamp(get_and_format_datetime_now())
        
        if not self.stop_queue.empty():
            logging.info(f"[MINER] I was asked to stop and i'm the miner {self.id}")
            self.stop_queue.get()
            self.result_queue.put((False, self.id))
            self.stats_writer.add_stat(self.id, False)
            self.ack_stop_queue.put(True)
            return False
        
        return True

    def run(self):
        while True:
            block = self.block_queue.get()
            is_mine_ok = self.mine(block)
            if is_mine_ok:
                miner_socket = Socket()
                miner_socket.connect(self.blockchain_host, self.blockchain_port)
                block_serialized = block.serialize()
                
                # send block to blockchain
                miner_socket.send_data(block_serialized)

                # receive result
                result = json.loads(miner_socket.recv_data())

                # write result in result_queue
                if result["result"] == "OK":
                    self.__handle_ok_result(result["hash"])
                else:
                    self.__handle_failed_result()

                miner_socket.close()

    def __handle_ok_result(self, hash_obtained):
        logging.info(f"[MINER] I'm the miner {self.id} and I could mine")
        logging.info(f"[MINER] Result from blockchain: {hash_obtained}")
        self.result_queue.put((True, self.id))
        self.prev_hash_queue.put(hash_obtained)
        self.stats_writer.add_stat(self.id, True)

    def __handle_failed_result(self):
        logging.info(f"[MINER] I'm the miner {self.id} and I couldn't mine")
        self.ack_stop_queue.put(True)
        self.result_queue.put((False, self.id))
        self.stats_writer.add_stat(self.id, False)
        