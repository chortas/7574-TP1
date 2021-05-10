import pytest
from common.block import Block
from queue import Queue
from time import sleep
import sys
from miner_manager.block_builder import BlockBuilder

class TestBlockBuilder:
    def setup_method(self):
        self.chunk_queue = Queue()
        self.block_queue = Queue()
        self.block_builder = BlockBuilder(self.chunk_queue, self.block_queue, 5)
        self.stop_flag = False
        self.block_builder.start()

    def test_doesnt_create_block_if_less_than_maximum(self):
        self.stop_flag = False
        self.chunk_queue.put("1")
        assert self.block_queue.empty()
        self.stop_flag = True
        self.chunk_queue.task_done()

    def test_create_one_block(self):
        entries = []
        for i in range(255):
            entries.append(str(i))
            self.chunk_queue.put(str(i))
            assert self.block_queue.empty()
        self.chunk_queue.put('256')
        entries.append('256')
        block = self.block_queue.get()
        assert block.get_entries() == entries

    def test_create_two_blocks(self):
        entries = []
        for i in range(255):
            entries.append(str(i))
            self.chunk_queue.put(str(i))
            assert self.block_queue.empty()
        self.chunk_queue.put('256')
        entries.append('256')
        block = self.block_queue.get()
        assert block.get_entries() == entries
        
        other_entries = []
        for i in range(257, 257+255):
            other_entries.append(str(i))
            self.chunk_queue.put(str(i))
            assert self.block_queue.empty()
        self.chunk_queue.put(str(257+255))
        other_entries.append(str(257+255))
        other_block = self.block_queue.get()
        assert other_block.get_entries() == other_entries

    def test_create_block_if_more_than_timeout(self):
        for i in range(5): 
            self.chunk_queue.put(str(i))
            assert self.block_queue.empty()
        sleep(15)
        block = self.block_queue.get()
        assert block != None
        assert block.get_entries() == ['0', '1', '2', '3', '4']

