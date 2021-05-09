from common.block import Block
from datetime import datetime

MAXIMUM_CHUNKS_BY_BLOCK = 256
MAX_WAIT_TIME = 10 

class BlockBuilder:
    def __init__(self):
        self.chunks = []
        self.start_time = datetime.now()
    
    def add_chunk(self, chunk):
        self.chunks.append(chunk)
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if len(self.chunks) >= MAXIMUM_CHUNKS_BY_BLOCK or elapsed_time >= MAX_WAIT_TIME:
            # the block is built and it should be returned
            block = Block(self.chunks)
            self.start_time = datetime.now()
            self.chunks = []
            return block
