import datetime
from cryptographic_solver import CryptographicSolver
from threading import Thread

# It should have a thread mining and a thread listening whether it needs to stop mining the block

class Miner(Thread):
    def __init__(self, block_queue, stop_queue, result_queue, miner_id):
        Thread.__init__(self)
        self.cryptographic_solver = CryptographicSolver()
        self.block_queue = block_queue
        self.stop_queue = stop_queue
        self.result_queue = result_queue
        self.id = miner_id

    def mine(self, block):
        block.set_timestamp(datetime.datetime.now())
        while not self.cryptographic_solver.solve(block) and not self.stop_queue.empty():
            block.add_nonce()
            block.set_timestamp(datetime.datetime.now())
        
        if not self.stop_queue.empty():
            print(f"Me pidieron que frene y soy el minero {self.id}")
            self.stop_queue.get()
            self.result_queue.put(False)
            return False
        
        self.result_queue.put(True)
        return True

    def run(self):
       while True:
            block = self.block_queue.get()
            result_mining = self.mine(block)
            if result_mining:
                pass
                # send to blockchain
            print("TASK DONE")
            self.block_queue.task_done()
             # TODO: delete this when its done and send this to blockchain manager
