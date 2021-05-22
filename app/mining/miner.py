from multiprocessing import Process
from queue import Empty
import json
import logging

from common.cryptographic_solver import CryptographicSolver
from sockets.socket import Socket
from common.utils import *

class Miner(Process):
    """Class that mines a block"""

    def __init__(self, block_queue, stop_queue, result_queue, miner_id, 
    blockchain_host, blockchain_port, stats, ack_stop_queue):
        Process.__init__(self)
        self.cryptographic_solver = CryptographicSolver()
        self.block_queue = block_queue
        self.stop_queue = stop_queue
        self.result_queue = result_queue
        self.id = miner_id
        self.blockchain_host = blockchain_host
        self.blockchain_port = blockchain_port
        self.stats = stats
        self.ack_stop_queue = ack_stop_queue
        self.should_stop = False

    def stop(self):
        self.should_stop = True
        empty_queue(self.block_queue)
        empty_queue(self.stop_queue)
        empty_queue(self.result_queue)
        empty_queue(self.ack_stop_queue)

    def run(self):
        while not self.should_stop:
            try:
                block = self.block_queue.get(timeout=OPERATION_TIMEOUT)
                self.__mine_block_and_handle_result(block)     
            except (Empty, OSError):
                self.stop()
        logging.info("[MINER] End run")

    def __mine_block_and_handle_result(self, block):
        is_mine_ok = self.__mine(block)
        if not is_mine_ok:
            return
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

    def __mine(self, block):
        block.set_timestamp(get_and_format_datetime_now())
        while not self.cryptographic_solver.solve(block, block.hash()) and self.stop_queue.empty():
            block.add_nonce()
            block.set_timestamp(get_and_format_datetime_now())
        
        if not self.stop_queue.empty():
            logging.info(f"[MINER] I was asked to stop and i'm the miner {self.id}")
            self.stop_queue.get()
            self.result_queue.put((None, self.id))
            self.stats.write_stat(self.id, False)
            self.ack_stop_queue.put(True)
            return False
        
        return True

    def __handle_ok_result(self, hash_obtained):
        logging.info(f"[MINER] I'm the miner {self.id} and I could mine")
        logging.info(f"[MINER] Result from blockchain: {hash_obtained}")
        self.result_queue.put((hash_obtained, self.id))
        self.stats.write_stat(self.id, True)

    def __handle_failed_result(self):
        logging.info(f"[MINER] I'm the miner {self.id} and I couldn't mine")
        self.ack_stop_queue.put(True)
        self.result_queue.put((None, self.id))
        self.stats.write_stat(self.id, False)
        