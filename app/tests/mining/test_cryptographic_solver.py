import pytest
from unittest.mock import Mock
from common.block import Block
from mining.cryptographic_solver import CryptographicSolver

class TestCryptographicSolver:

    def test_solve_ok(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.hash.return_value = 1
        block.get_difficulty.return_value = 1
        assert cryptographic_solver.solve(block)

    def test_solve_wrong(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.hash.return_value = 2**256
        block.get_difficulty.return_value = 1
        assert not cryptographic_solver.solve(block)

    def test_solve_ok_with_high_hash(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.hash.return_value = 2**255
        block.get_difficulty.return_value = 1
        assert cryptographic_solver.solve(block)
    
    def test_solve_wrong_with_difficulty(self):
        block = Mock()
        cryptographic_solver = CryptographicSolver()
        block.hash.return_value = 2**255
        block.get_difficulty.return_value = 2
        assert not cryptographic_solver.solve(block)
        