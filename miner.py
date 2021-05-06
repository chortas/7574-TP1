import datetime

# It should have a thread mining and a thread listening whether it needs to stop mining the thread

class Miner:
    def isCryptographicPuzzleSolved(block):
        return block.hash() < (2**256) / block.get_difficulty() - 1

    def mine(prev_hash, block):
        block.set_prev_hash(prev_hash)
        block.set_timestamp(datetime.datetime.now())
        while not isCryptographicPuzzleSolved(block):
            block.add_nonce()
            block.set_timestamp(datetime.datetime.now())
            
        # to know prev_hash() for future interactions
        return block.hash()
