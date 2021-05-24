import pytest
from common.block import Block
from common.cryptographic_solver import CryptographicSolver

class TestCryptographicSolver:

    def test_solve_ok(self):
        block = Block(())
        cryptographic_solver = CryptographicSolver()
        block.difficulty = 1
        assert cryptographic_solver.solve(block, 1)

    def test_solve_wrong(self):
        block = Block(())
        cryptographic_solver = CryptographicSolver()
        block.difficulty = 1
        assert not cryptographic_solver.solve(block, 2**256)

    def test_solve_ok_with_high_hash(self):
        block = Block(())
        cryptographic_solver = CryptographicSolver()
        block.difficulty = 1
        assert cryptographic_solver.solve(block, 2*255)
    
    def test_solve_wrong_with_difficulty(self):
        block = Block(())
        cryptographic_solver = CryptographicSolver()
        block.difficulty = 2
        assert not cryptographic_solver.solve(block, 2**255)
        