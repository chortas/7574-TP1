from common.block import Block

MAXIMUM_CHUNKS_BY_BLOCK = 256

class BlockBuilder:
    def __init__(self):
        self.chunks = []
    
    def add_chunk(self, chunk):
        self.chunks.append(chunk)
        if len(self.chunks) >= MAXIMUM_CHUNKS_BY_BLOCK:
            # the block is built and it should be returned
            block = Block(self.chunks)
            self.chunks = []
            return block
        