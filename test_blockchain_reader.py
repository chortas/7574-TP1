import pytest
import csv
import os
from blockchain_reader import BlockchainReader
from datetime import datetime

class TestBlockchainReader:
    def test_get_right_block(self):
        block_hash = 1
        block_prev_hash = 0
        block_nonce = 1
        block_timestamp = datetime(2020, 5, 17, 22, 30)
        block_difficulty = 1
        block_entries = ['entry', 'other entry']

        with open('1.csv', mode='w') as block_file:
            fieldnames = ['hash', 'prev_hash', 'nonce', 'timestamp', 'entries_amount', 'difficulty', 'entries']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': block_hash, 
                            'prev_hash': block_prev_hash, 
                            'nonce': block_nonce, 
                            'timestamp': block_timestamp, 
                            'entries_amount': len(block_entries), 
                            'difficulty': block_difficulty, 
                            'entries': 'entry-other entry'
                            })
        
        blockchain_reader = BlockchainReader()
        block = blockchain_reader.get_block(block_hash)
        assert block.get_prev_hash() == block_prev_hash
        assert block.get_nonce() == block_nonce
        assert block.get_timestamp() == block_timestamp 
        assert block.get_difficulty() == block_difficulty
        assert block.get_entries() == block_entries

        os.remove('1.csv')