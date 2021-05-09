import pytest
import os
import csv
from datetime import datetime
from common.block import Block
from blockchain.blockchain_writer import BlockchainWriter

class TestBlockchainWriter:
    def setup_method(self, method):
        self.block = Block([])
        self.timestamp = datetime(2020, 5, 17, 22, 30)
        self.block.set_timestamp(self.timestamp)

    def teardown_method(self, method):
        hash_file_name = str(self.block.hash()) + '.csv'
        day_file_name = '2020-05-17.csv'
        os.remove(hash_file_name)
        os.remove(day_file_name)
        
    def test_file_name_is_hash_and_day(self):
        hash_file_name = str(self.block.hash()) + '.csv'
        day_file_name = '2020-05-17.csv'

        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(self.block)
        assert os.path.exists(hash_file_name)
        assert os.path.exists(day_file_name)
    
    def test_write_block_ok(self):
        prev_hash = 12
        entry = 'entry'
        other_entry ='other entry'

        self.block.set_prev_hash(prev_hash)
        self.block.add_nonce()
        self.block.add_entry(entry)
        self.block.add_entry(other_entry)

        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(self.block)
        
        hash_file_name = str(self.block.hash()) + '.csv'
        day_file_name = '2020-05-17.csv'

        with open(hash_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                assert row['hash'] == str(self.block.hash())
                assert row['prev_hash'] == str(prev_hash)
                assert row['nonce'] == str(1) 
                assert row['timestamp'] == str(self.timestamp)
                assert row['entries_amount'] == str(2)
                assert row['difficulty'] == str(1)
                assert row['entries'] == entry + '-' + other_entry

        with open(day_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                assert row['hash'] == str(self.block.hash())
                assert row['timestamp'] == str(self.timestamp)
  
    def test_add_other_block_with_same_day(self):
        other_block = Block(['otherEntry'])
        other_timestamp = datetime(2020, 5, 17, 23, 30)
        other_block.set_timestamp(other_timestamp)

        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(self.block)
        blockchain_writer.write_block(other_block)
        
        block_hash_file_name = str(self.block.hash()) + '.csv'
        other_block_hash_file_name = str(other_block.hash()) + '.csv'

        assert os.path.exists(block_hash_file_name)
        assert os.path.exists(other_block_hash_file_name)
        os.remove(other_block_hash_file_name)

        day_file_name = '2020-05-17.csv'
        with open(day_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    assert row['hash'] == str(self.block.hash())
                    assert row['timestamp'] == str(self.timestamp)
                else:
                    assert row['hash'] == str(other_block.hash())
                    assert row['timestamp'] == str(other_timestamp)
                line_count += 1
    
    def test_add_other_block_with_other_day(self):
        other_block = Block(['otherEntry'])
        other_timestamp = datetime(2020, 5, 18, 23, 30)
        other_block.set_timestamp(other_timestamp)

        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(self.block)
        blockchain_writer.write_block(other_block)
        
        block_hash_file_name = str(self.block.hash()) + '.csv'
        other_block_hash_file_name = str(other_block.hash()) + '.csv'

        assert os.path.exists(block_hash_file_name)
        assert os.path.exists(other_block_hash_file_name)
        os.remove(other_block_hash_file_name)
        
        other_day_file_name = '2020-05-18.csv'
        assert os.path.exists(other_day_file_name)

        with open(other_day_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:        
                assert row['hash'] == str(other_block.hash())
                assert row['timestamp'] == str(other_timestamp)
        
        os.remove(other_day_file_name)
