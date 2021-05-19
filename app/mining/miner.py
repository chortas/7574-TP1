import datetime
from threading import Thread
import socket
import json
import logging
from common.cryptographic_solver import CryptographicSolver
from sockets.socket import Socket
from common.utils import *
from stats.stats_writer import StatsWriter

class Miner(Thread):
    """Class that mines a block"""

    def __init__(self, block_queue, stop_queue, result_queue, miner_id, 
    blockchain_host, blockchain_port, prev_hash_queue, stats_writer):
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

    def mine(self, block):
        block.set_timestamp(get_and_format_datetime_now())
        while not self.cryptographic_solver.solve(block, block.hash()) and self.stop_queue.empty():
            block.add_nonce()
            block.set_timestamp(get_and_format_datetime_now())
        
        if not self.stop_queue.empty():
            logging.info(f"[MINER] I was asked to stop and i'm the miner {self.id}")
            self.stop_queue.get()
            self.result_queue.put(False)
            self.stats_writer.add_stat(self.id, False)
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
                    logging.info(f"[MINER] I'm the miner {self.id} and I could mine")
                    logging.info(f"[MINER] Result from blockchain: {result}")
                    self.result_queue.put(True)
                    hash_obtained = result["hash"]
                    self.prev_hash_queue.put(hash_obtained)
                    self.stats_writer.add_stat(self.id, True)
                else:
                    logging.info(f"[MINER] I'm the miner {self.id} and I couldn't mine")
                    self.result_queue.put(False)
                    self.stats_writer.add_stat(self.id, False)

                miner_socket.close()
            self.block_queue.task_done()
