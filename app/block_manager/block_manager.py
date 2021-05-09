from queue import Queue
from miner import Miner
from threading import Thread
from difficulty_adjuster import DifficultyAdjuster
from stats.stats_writer import StatsWriter

import time
import logging

class BlockManager:
    def __init__(self, n_miners, blockchain_host, blockchain_port):
        self.n_miners = n_miners
        self.block_queues = [Queue() for _ in range(n_miners)]
        self.stop_queues = [Queue() for _ in range(n_miners)]
        self.result_queues = [Queue() for _ in range(n_miners)]
        self.prev_hash_queues = [Queue() for _ in range(n_miners)]
        self.miners = [Miner(self.block_queues[i], self.stop_queues[i], 
        self.result_queues[i], i, blockchain_host, blockchain_port, self.prev_hash_queues[i],
        StatsWriter(self.n_miners)) for i in range(n_miners)]
        self.receiver_results = [Thread(target=self.receive_results, args=(i,)) for i in range(n_miners)]
        self.prev_hash = 0
        self.difficulty_adjuster = DifficultyAdjuster()

        self.start_threads()

    def send_block(self, block):
        block.set_prev_hash(self.prev_hash)
        block.set_difficulty(self.difficulty_adjuster.get_difficulty())
        logging.info(f"La dificultad del bloque que estoy por mandar es: {block.get_difficulty()}")
        logging.info(f"I'm about to send the block: {block}")
        for block_queue in self.block_queues:
            block_queue.put(block)
            block_queue.join()

    def start_threads(self):
        for i in range(self.n_miners):
            self.miners[i].start()
            self.receiver_results[i].start()

    def receive_results(self, id_miner):
        while True:
            # listen result from result_queues
            could_mine = self.result_queues[id_miner].get()
            if could_mine:
                logging.info(f"El minero {id_miner} pudo minar")
                self.stop_miners_except(id_miner)
                self.prev_hash = self.prev_hash_queues[id_miner].get()
                self.difficulty_adjuster.add_block_to_count()
            else:
                logging.info(f"El minero {id_miner} no pudo minar")
    
    def stop_miners_except(self, id_miner):
        for i in range(self.n_miners):
            if i != id_miner:
                self.stop_queues[i].put(True)

    def join(self):
        for i in range(self.n_miners):
            self.miners[i].join()
            self.receiver_results[i].join()