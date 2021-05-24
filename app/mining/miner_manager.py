import logging
from multiprocessing import Queue
from queue import Empty
from threading import Thread
from copy import copy

from miner import Miner
from difficulty_adjuster import DifficultyAdjuster
from common.utils import *

class MinerManager(Thread):
    """Class that communicates with the miners in order to mine blocks"""

    def __init__(self, n_miners, blockchain_host, blockchain_port, block_queue, stats, graceful_stopper):
        Thread.__init__(self)
        self.n_miners = n_miners
        self.miner_block_queues = [Queue() for _ in range(n_miners)]
        self.stop_queues = [Queue() for _ in range(n_miners)]
        self.result_queue = Queue()
        self.ack_stop_queue = Queue()
        self.miners = [Miner(self.miner_block_queues[i], self.stop_queues[i], self.result_queue, 
        i, blockchain_host, blockchain_port, stats, self.ack_stop_queue) 
        for i in range(n_miners)]
        self.prev_hash = 0
        self.difficulty_adjuster = DifficultyAdjuster()
        self.block_queue = block_queue
        self.graceful_stopper = graceful_stopper
        
    def run(self):
        self.__start_threads()
        while not self.graceful_stopper.has_been_stopped():
            try:
                block = self.block_queue.get(timeout=OPERATION_TIMEOUT)
                block.prev_hash = self.prev_hash
                block.difficulty = self.difficulty_adjuster.get_difficulty()
                queues_to_send = self.miner_block_queues[:]
                for block_queue in queues_to_send:
                    logging.info("[MINER_MANAGER] Puting block in queue...")
                    block_queue.put(copy(block))
                self.__receive_results() #block until all results come back from blockchain
            except Empty:
                self.__stop()
        logging.info("[MINER_MANAGER] End run")
    
    def __stop(self):
        self.graceful_stopper.exit_gracefully()
        for queue in self.miner_block_queues:
            empty_queue(queue)
        for queue in self.stop_queues:
            empty_queue(queue)
        empty_queue(self.result_queue)
        empty_queue(self.ack_stop_queue)
        empty_queue(self.block_queue)
        for miner in self.miners:
            miner.stop()

    def __start_threads(self):
        for i in range(self.n_miners):
            self.miners[i].start()

    def __receive_results(self):
        for _ in range(self.n_miners):
            hash_obtained, id_miner = self.result_queue.get()
            if hash_obtained != None:
                logging.info(f"[MINER_MANAGER] The miner {id_miner} could mine with hash {hash_obtained}")
                self.__stop_miners(id_miner)
                self.prev_hash = hash_obtained
                self.difficulty_adjuster.add_block_to_count()
    
    def __stop_miners(self, id_miner):
        for id in range(self.n_miners):
            if id != id_miner:
                self.stop_queues[id].put(True)
        for _ in range(self.n_miners - 1):
            self.ack_stop_queue.get()
        self.__clear_queues()
       
    def __clear_queues(self):
        for id in range(self.n_miners):
            queue = self.stop_queues[id]
            if not queue.empty():
                queue.get()
        