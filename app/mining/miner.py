import datetime
from mining.cryptographic_solver import CryptographicSolver
from threading import Thread

# It should have a thread mining and a thread listening whether it needs to stop mining the block

class Miner:
    def __init__(self, block_queue, stop_queue, result_queue):
        self.cryptographic_solver = CryptographicSolver()
        self.block_queue = block_queue
        self.stop_queue = stop_queue
        self.result_queue = result_queue

    def mine(self, block):
        block.set_timestamp(datetime.datetime.now())
        while not self.cryptographic_solver.solve(block):
            block.add_nonce()
            block.set_timestamp(datetime.datetime.now())
            
        # to know prev_hash() for future interactions
        return block.hash()

    def run(self):
      while True:
        block = self.block_queue.get()
        self.mine(block)
        break # TODO: delete this when its done
