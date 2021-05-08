import csv
import os
from datetime import datetime
from block import Block

class BlockchainReader:
    def get_block(self, block_hash):
        hash_file_name = str(block_hash) + '.csv'

        if not os.path.exists(hash_file_name):
            raise ValueError("There's no block with that hash")

        header = {}
        entries = []

        with open(hash_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                header = {
                    'prev_hash': int(row['prev_hash']), 
                    'nonce': int(row['nonce']),
                    'timestamp': datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                    'entries_amount': int(row['entries_amount']),
                    'difficulty': int(row['difficulty'])
                }
                entries = row['entries'].split('-')

        # todo - maybe its needed to serialize
        return Block(entries, header)

