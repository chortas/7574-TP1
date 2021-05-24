class CryptographicSolver:
    """Class that encapsulates the problem to solve in order to add a block to a blockchain"""
    def solve(self, block, hash_block):
        return hash_block < (2**256) / block.difficulty - 1
