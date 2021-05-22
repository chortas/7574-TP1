import logging
from queue import Empty
from threading import Thread

from common.block import Block
from common.utils import *

MAXIMUM_CHUNKS_BY_BLOCK = 256

class BlockBuilder(Thread):
    """Class that builds a block given chunks"""

    def __init__(self, chunk_queue, block_queue, timeout_chunk):
        Thread.__init__(self)
        self.chunk_queue = chunk_queue
        self.block_queue = block_queue
        self.chunks = []
        self.timeout_chunk = timeout_chunk
        self.should_stop = False

    def stop(self):
        self.should_stop = True
        empty_queue(self.chunk_queue)
        empty_queue(self.block_queue)
    
    def run(self):
        while not self.should_stop:
            chunk = None
            try:
                chunk = self.chunk_queue.get(timeout=self.timeout_chunk) 
                self.chunks.append(chunk)
                if len(self.chunks) == MAXIMUM_CHUNKS_BY_BLOCK:
                    logging.info("[BLOCK_BUILDER] Block is completed and it will be sent")
                    self.__build_and_send_block()
            except Empty:
                if len(self.chunks) != 0:
                    logging.info("[BLOCK_BUILDER] Timeout has expired and the block will be sent anyway")
                    self.__build_and_send_block()
        logging.info("[BLOCK_BUILDER] End run")

    def __build_and_send_block(self):
        block = Block(self.chunks)
        self.chunks = []
        self.block_queue.put(block)

