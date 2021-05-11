from queue import Queue
from miner import Miner
from threading import Thread
from difficulty_adjuster import DifficultyAdjuster
from stats.stats_writer import StatsWriter

import time
import logging
from random import shuffle

class MinerManager(Thread):
    """Class that communicates with the miners in order to mine blocks"""

    def __init__(self, n_miners, blockchain_host, blockchain_port, block_queue):
        Thread.__init__(self)
        self.n_miners = n_miners
        self.miner_block_queues = [Queue() for _ in range(n_miners)]
        self.stop_queues = [Queue() for _ in range(n_miners)]
        self.result_queues = [Queue() for _ in range(n_miners)]
        self.prev_hash_queues = [Queue() for _ in range(n_miners)]
        self.miners = [Miner(self.miner_block_queues[i], self.stop_queues[i], 
        self.result_queues[i], i, blockchain_host, blockchain_port, self.prev_hash_queues[i],
        StatsWriter(self.n_miners)) for i in range(n_miners)]
        self.receiver_results = [Thread(target=self.receive_results, args=(i,)) for i in range(n_miners)]
        self.prev_hash = 0
        self.difficulty_adjuster = DifficultyAdjuster()
        self.block_queue = block_queue

        self.start_threads()

    def get_block_queue(self):
        return self.block_queue
        
    def run(self):
        while True:
            block = self.block_queue.get()
            block.set_prev_hash(self.prev_hash)
            block.set_difficulty(self.difficulty_adjuster.get_difficulty())
            queues_to_send = self.miner_block_queues[:]
            shuffle(queues_to_send)
            for block_queue in queues_to_send:
                block_queue.put(block)
                block_queue.join()

    def start_threads(self):
        for i in range(self.n_miners):
            self.miners[i].start()
            self.receiver_results[i].start()

    def receive_results(self, id_miner):
        while True:
            could_mine = self.result_queues[id_miner].get()
            if could_mine:
                logging.info(f"[MINER_MANAGER] The miner {id_miner} could mine")
                self.stop_miners_except(id_miner)
                self.prev_hash = self.prev_hash_queues[id_miner].get()
                self.difficulty_adjuster.add_block_to_count()
            else:
                logging.info(f"[MINER_MANAGER] The miner {id_miner} couldn't mine")
    
    def stop_miners_except(self, id_miner):
        for i in range(self.n_miners):
            if i != id_miner:
                self.stop_queues[i].put(True)
