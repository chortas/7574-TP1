import datetime
from cryptographic_solver import CryptographicSolver

# It should have a thread mining and a thread listening whether it needs to stop mining the block

class Miner:
    def __init__(self):
        self.cryptographic_solver = CryptographicSolver()

    def mine(self, prev_hash, block):
        block.set_prev_hash(prev_hash)
        block.set_timestamp(datetime.datetime.now())
        while not self.cryptographic_solver.solve(block):
            block.add_nonce()
            block.set_timestamp(datetime.datetime.now())
            
        # to know prev_hash() for future interactions
        return block.hash()
