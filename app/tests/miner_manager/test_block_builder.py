import pytest
from common.block import Block
from time import sleep
from miner_manager.block_builder import BlockBuilder

class TestCryptographicSolver:
    def setup_method(self):
        self.block_builder = BlockBuilder()

    def test_doesnt_create_block_if_less_than_maximum(self):
        for i in range(5):
            block = self.block_builder.add_chunk(str(i))
            assert block == None

    def test_doesnt_create_one_block(self):
        entries = []
        for i in range(255):
            entries.append(str(i))
            block = self.block_builder.add_chunk(str(i))
            assert block == None
        block = self.block_builder.add_chunk(str(256))
        assert block != None
        entries.append('256')
        assert block.get_entries() == entries

    def test_doesnt_create_two_blocks(self):
        entries = []
        for i in range(255):
            entries.append(str(i))
            block = self.block_builder.add_chunk(str(i))
            assert block == None
        block = self.block_builder.add_chunk('256')
        assert block != None
        entries.append('256')
        assert block.get_entries() == entries
        
        other_entries = []
        for i in range(257, 257+255):
            other_entries.append(str(i))
            block = self.block_builder.add_chunk(str(i))
            assert block == None
        other_block = self.block_builder.add_chunk(str(257+255))
        assert other_block != None
        other_entries.append(str(257+255))
        assert other_block.get_entries() == other_entries

    def test_create_block_if_more_than_timeout(self):
        for i in range(5):
            block = self.block_builder.add_chunk(str(i))
            assert block == None
        sleep(15)
        block = self.block_builder.add_chunk('5')
        assert block != None
        assert block.get_entries() == ['0', '1', '2', '3', '4', '5']
        