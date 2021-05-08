from queue import queue

class BlockManager:
    def __init__(self, n_miners):
        self.n_miners = n_miners
        self.block_queues = [Queue() for _ in range(n_miners)]
        self.stop_queues = [Queue() for _ in range(n_miners)]
        self.result_queues = [Queue() for _ in range(n_miners)]
        # make threads
        self.miners = [Miner(self.block_queues[i], self.stop_queues[i], self.result_queues[i]) for i in range(n_miners)]

    def send_block(self, block):
        # Block should have prev_hash
        for block_queue in self.block_queues:
            block_queue.put(block)
