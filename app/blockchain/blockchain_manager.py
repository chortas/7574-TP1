class BlockchainManager:
    def __init__(self):
        self.blocks = []
        self.last_block_hash = 0
        self.cryptographic_solver = CryptographicSolver()

    def addBlock(self, newBlock):
        # add communication with miner
        
        if (self.isBlockValid(newBlock)):
            self.blocks.append(newBlock)
            self.last_block_hash = newBlock.hash()
            return True
        return False
    
    def isBlockValid(self, block):
        return block.header.get_prev_hash() == self.last_block_hash and self.cryptographic_solver.solve(block)
    
    def getLastHash(self):
        return self.last_block_hash
    