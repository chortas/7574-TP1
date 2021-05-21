import logging
from multiprocessing import Queue
from threading import Thread

from miner import Miner
from difficulty_adjuster import DifficultyAdjuster
from stats.stats_writer import StatsWriter

class MinerManager(Thread):
    """Class that communicates with the miners in order to mine blocks"""

    def __init__(self, n_miners, blockchain_host, blockchain_port, block_queue):
        Thread.__init__(self)
        self.n_miners = n_miners
        self.miner_block_queues = [Queue() for _ in range(n_miners)]
        self.stop_queues = [Queue() for _ in range(n_miners)]
        self.result_queue = Queue()
        self.ack_stop_queue = Queue()
        self.miners = [Miner(self.miner_block_queues[i], self.stop_queues[i], self.result_queue, 
        i, blockchain_host, blockchain_port, StatsWriter(self.n_miners), self.ack_stop_queue) 
        for i in range(n_miners)]
        self.prev_hash = 0
        self.difficulty_adjuster = DifficultyAdjuster()
        self.block_queue = block_queue

        self.__start_threads()

    def get_block_queue(self):
        return self.block_queue
        
    def run(self):
        while True:
            block = self.block_queue.get()
            block.set_prev_hash(self.prev_hash)
            block.set_difficulty(self.difficulty_adjuster.get_difficulty())
            queues_to_send = self.miner_block_queues[:]
            for block_queue in queues_to_send:
                block_queue.put(block)
            self.__receive_results()

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
        