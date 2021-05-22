import csv
import os

class BlockchainWriter:
    """Class that writes information from the block on different files and indexes.
    There is one file for every hash_block and one file by day with the hash block and its
    timestamp (as an index)"""

    def __init__(self, block_index_lock, block_lock):
        self.block_index_lock = block_index_lock
        self.block_lock = block_lock
    
    def write_block(self, block):
        # file with hash and all information from block
        hash_file_name = str(block.hash()) + '.csv'
        self.__write_hash_file_safe(hash_file_name, block)

        # file with hash and timestamp by block
        block_day = block.get_day()
        day_file_name = block_day + '.csv'
        self.__write_day_file_safe(day_file_name, block)

    def __write_hash_file_safe(self, file_name, block):
        self.block_lock.acquire()
        try:
            self.__write_hash_file(file_name, block)
        finally:
            self.block_lock.release()

    def __write_day_file_safe(self, file_name, block):
        self.block_index_lock.acquire()
        try:
            self.__write_day_file(file_name, block)
        finally:
            self.block_index_lock.release()

    def __write_hash_file(self, file_name, block):
        with open(file_name, mode='w') as block_file:
            fieldnames = ['hash', 'prev_hash', 'nonce', 'timestamp', 'entries_amount', 'difficulty', 'entries']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow(block.serialize_into_dict())

    def __write_day_file(self, file_name, block):
        exists = os.path.exists(file_name)

        with open(file_name, mode='a') as block_file:
            fieldnames = ['hash', 'timestamp']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)

            if not exists:
                writer.writeheader()

            writer.writerow({'hash': block.hash(), 'timestamp': block.get_timestamp()})
            