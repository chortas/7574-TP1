import pytest
import os
import csv
from datetime import datetime
from block import Block
from blockchain_writer import BlockchainWriter

class TestBlockchainWriter:
    def test_file_name_is_hash(self):
        block = Block([])
        file_name = str(block.hash()) + '.csv'
        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(block)
        assert os.path.exists(file_name)
        os.remove(file_name)

    def test_write_block_ok(self):
        timestamp = datetime.now()
        prev_hash = 12
        entries = ['entry']

        block = Block(entries)

        block.set_timestamp(timestamp)
        block.set_prev_hash(prev_hash)
        block.add_nonce()

        blockchain_writer = BlockchainWriter()
        blockchain_writer.write_block(block)
        
        file_name = str(block.hash()) + '.csv'

        with open(file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                assert row['hash'] == str(block.hash())
                assert row['prev_hash'] == str(block.get_prev_hash())
                assert row['nonce'] == str(1) 
                assert row['timestamp'] == str(timestamp)
                assert row['entries_amount'] == str(len(entries))
                assert row['difficulty'] == str(1)
                assert row['entries'] == str(entries)

        os.remove(file_name)
    