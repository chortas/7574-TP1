import pytest
from block import Block
from miner import Miner

class TestMiner:
    def test_mine_works(self):
        miner = Miner()
        block = Block([])
        hash_mined = miner.mine(1, block)
        assert hash_mined == -1