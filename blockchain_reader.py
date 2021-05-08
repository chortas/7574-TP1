import csv
import os
from datetime import datetime, timedelta
from block import Block

class BlockchainReader:
    def get_block(self, block_hash):
        hash_file_name = str(block_hash) + '.csv'

        if not os.path.exists(hash_file_name):
            return None

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

        return Block(entries, header)

    def get_blocks_between_minute_interval(self, first_endpoint):
        blocks = []
        second_endpoint = first_endpoint + timedelta(minutes=1)

        day = first_endpoint.strftime("%m-%d-%Y")
        file_name = str(day) + '.csv'

        if not os.path.exists(file_name): 
            return blocks
        with open(file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                if timestamp >= first_endpoint and timestamp <= second_endpoint:
                    block_hash = int(row['hash'])
                    blocks.append(self.get_block(block_hash))

        return blocks
        