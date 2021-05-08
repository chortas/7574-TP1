import pytest
import csv
import os
from blockchain.blockchain_reader import BlockchainReader
from datetime import datetime

class TestBlockchainReader:
    def test_get_right_block_by_hash(self):
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

    def test_raise_exception_if_block_doesnt_exist(self):
        blockchain_reader = BlockchainReader()
        block = blockchain_reader.get_block(10000)
        assert block == None

    def test_get_no_blocks_if_file_doesnt_exist(self):
        first_endpoint = datetime(2020, 5, 17, 22, 30)
        
        blockchain_reader = BlockchainReader()
        blocks = blockchain_reader.get_blocks_between_minute_interval(first_endpoint)
   
        assert len(blocks) == 0
    
    def test_get_right_block_by_interval(self):
        block_hash = 1
        block_prev_hash = 0
        block_nonce = 1
        block_timestamp = datetime(2020, 5, 17, 22, 30, 5)
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
        
        with open('05-17-2020.csv', mode='w') as block_file:
            fieldnames = ['hash', 'timestamp']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': block_hash, 
                            'timestamp': block_timestamp
                            })

        blockchain_reader = BlockchainReader()
        first_endpoint = datetime(2020, 5, 17, 22, 30)
        blocks = blockchain_reader.get_blocks_between_minute_interval(first_endpoint)

        assert len(blocks) == 1

        block = blocks[0]

        assert block.get_prev_hash() == block_prev_hash
        assert block.get_nonce() == block_nonce
        assert block.get_timestamp() == block_timestamp 
        assert block.get_difficulty() == block_difficulty
        assert block.get_entries() == block_entries

        os.remove('1.csv')
        os.remove('05-17-2020.csv')
    
    def test_get_no_block_by_interval(self):
        block_hash = 1
        block_prev_hash = 0
        block_nonce = 1
        block_timestamp = datetime(2020, 5, 17, 22, 30, 5)
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
        
        with open('05-17-2020.csv', mode='w') as block_file:
            fieldnames = ['hash', 'timestamp']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': block_hash, 
                            'timestamp': block_timestamp
                            })

        blockchain_reader = BlockchainReader()
        first_endpoint = datetime(2020, 5, 17, 22, 35)
        blocks = blockchain_reader.get_blocks_between_minute_interval(first_endpoint)
        assert len(blocks) == 0

    def test_get_right_blocks_by_interval(self):
        block_hash = 1
        other_block_hash = 2
        block_prev_hash = 0
        other_block_prev_hash = 1
        block_nonce = 1
        other_block_nonce = 2
        block_timestamp = datetime(2020, 5, 17, 22, 30, 5)
        other_block_timestamp = datetime(2020, 5, 17, 22, 30, 8)
        block_difficulty = 1
        other_block_difficulty = 2
        block_entries = ['entry', 'other entry']
        other_block_entries = ['some entry']

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
        
        with open('2.csv', mode='w') as block_file:
            fieldnames = ['hash', 'prev_hash', 'nonce', 'timestamp', 'entries_amount', 'difficulty', 'entries']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': other_block_hash, 
                            'prev_hash': other_block_prev_hash, 
                            'nonce': other_block_nonce, 
                            'timestamp': other_block_timestamp, 
                            'entries_amount': len(other_block_entries), 
                            'difficulty': other_block_difficulty, 
                            'entries': 'some entry'
                            })
            

        with open('05-17-2020.csv', mode='w') as block_file:
            fieldnames = ['hash', 'timestamp']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': block_hash, 
                            'timestamp': block_timestamp
                            })
            writer.writerow({'hash': other_block_hash, 
                            'timestamp': other_block_timestamp
                            })

        blockchain_reader = BlockchainReader()
        first_endpoint = datetime(2020, 5, 17, 22, 30)
        blocks = blockchain_reader.get_blocks_between_minute_interval(first_endpoint)

        assert len(blocks) == 2

        block = blocks[0]

        assert block.get_prev_hash() == block_prev_hash
        assert block.get_nonce() == block_nonce
        assert block.get_timestamp() == block_timestamp 
        assert block.get_difficulty() == block_difficulty
        assert block.get_entries() == block_entries

        other_block = blocks[1]

        assert other_block.get_prev_hash() == other_block_prev_hash
        assert other_block.get_nonce() == other_block_nonce
        assert other_block.get_timestamp() == other_block_timestamp 
        assert other_block.get_difficulty() == other_block_difficulty
        assert other_block.get_entries() == other_block_entries

        os.remove('1.csv')
        os.remove('2.csv')
        os.remove('05-17-2020.csv')
    