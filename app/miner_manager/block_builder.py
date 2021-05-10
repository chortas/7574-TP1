from common.block import Block
from queue import Empty
from threading import Thread
import logging

MAXIMUM_CHUNKS_BY_BLOCK = 256
MAX_WAIT_TIME = 15

class BlockBuilder(Thread):
    def __init__(self, chunk_queue, block_queue):
        Thread.__init__(self)
        self.chunk_queue = chunk_queue
        self.block_queue = block_queue
        self.chunks = []
    
    def run(self):
        while True:
            chunk = None
            try:
                chunk = self.chunk_queue.get(timeout=MAX_WAIT_TIME) 
                self.chunks.append(chunk)
                if len(self.chunks) == MAXIMUM_CHUNKS_BY_BLOCK:
                    logging.info("Block is completed and it will be sent")
                    self.__build_and_send_block()
            except Empty:
                if len(self.chunks) != 0:
                    logging.info("Timeout has expired and the block will be sent anyway")
                    self.__build_and_send_block()

    def __build_and_send_block(self):
        block = Block(self.chunks)
        self.chunks = []
        self.block_queue.put(block)