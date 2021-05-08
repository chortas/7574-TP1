import csv
import os

class BlockchainWriter:
    def write_block(self, block):
        # file with hash and all information from block
        hash_file_name = str(block.hash()) + '.csv'
        self.__write_hash_file(hash_file_name, block)

        # file with hash and timestamp by block
        block_day = block.get_day()
        day_file_name = block_day + '.csv'
        self.__write_day_file(day_file_name, block)
        
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