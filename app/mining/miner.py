from multiprocessing import Process
from queue import Empty
from socket import *
import json
import logging

from common.cryptographic_solver import CryptographicSolver
from sockets.socket import Socket
from common.utils import *

class Miner(Process):
    """Class that mines a block"""

    def __init__(self, block_queue, stop_queue, result_queue, miner_id, 
    blockchain_host, blockchain_port, stats, ack_stop_queue, kill_queue):
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
        self.kill_queue = kill_queue

    def run(self):
        while self.kill_queue.empty():
            miner_socket = None
            try:
                block = self.block_queue.get(timeout=OPERATION_TIMEOUT)
                is_mine_ok = self.__mine(block)
                if is_mine_ok:
                    miner_socket = Socket()
                    self.__handle_result(block, miner_socket)     
            except (Empty, timeout):
                if not self.kill_queue.empty():
                    self.__stop()
                    break
            except OSError as e:
                logging.info(f"[MINER #{self.id}] Error while operating with socket: {e}")
            finally: 
                if miner_socket != None:
                    miner_socket.close()
        logging.info(f"[MINER #{self.id}] End run")

    def __stop(self):
        empty_queue(self.kill_queue)
        empty_queue(self.block_queue)
        empty_queue(self.stop_queue)
        empty_queue(self.result_queue)
        empty_queue(self.ack_stop_queue)

    def __mine(self, block):
        block.timestamp = get_and_format_datetime_now()
        while not self.cryptographic_solver.solve(block, block.compute_hash()) and self.stop_queue.empty() and self.kill_queue.empty():
            block.add_nonce()
            block.timestamp = get_and_format_datetime_now()
        
        if not self.stop_queue.empty():
            logging.info(f"[MINER #{self.id}] I was asked to stop mining")
            self.stop_queue.get()
            self.result_queue.put((None, self.id))
            self.stats.write_stat(self.id, False)
            self.ack_stop_queue.put(True)
            return False
        
        return self.kill_queue.empty()

    def __handle_result(self, block, miner_socket):
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

    def __handle_ok_result(self, hash_obtained):
        logging.info(f"[MINER #{self.id}] I could mine")
        logging.info(f"[MINER #{self.id}] Result from blockchain: {hash_obtained}")
        self.result_queue.put((hash_obtained, self.id))
        self.stats.write_stat(self.id, True)

    def __handle_failed_result(self):
        logging.info(f"[MINER #{self.id}] I couldn't mine")
        self.ack_stop_queue.put(True)
        self.result_queue.put((None, self.id))
        self.stats.write_stat(self.id, False)
        