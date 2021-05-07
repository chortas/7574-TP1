class CryptographicSolver:
    def solve(self, block):
        return block.hash() < (2**256) / block.get_difficulty() - 1
