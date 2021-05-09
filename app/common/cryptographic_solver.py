class CryptographicSolver:
    def solve(self, block, hash_block):
        return hash_block < (2**256) / block.get_difficulty() - 1
