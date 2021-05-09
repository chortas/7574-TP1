import pytest
from unittest.mock import Mock
from common.block import Block
from common.cryptographic_solver import CryptographicSolver

class TestCryptographicSolver:

    def test_solve_ok(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.get_difficulty.return_value = 1
        assert cryptographic_solver.solve(block, 1)

    def test_solve_wrong(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.get_difficulty.return_value = 1
        assert not cryptographic_solver.solve(block, 2**256)

    def test_solve_ok_with_high_hash(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.get_difficulty.return_value = 1
        assert cryptographic_solver.solve(block, 2*255)
    
    def test_solve_wrong_with_difficulty(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.get_difficulty.return_value = 2
        assert not cryptographic_solver.solve(block, 2**255)
        