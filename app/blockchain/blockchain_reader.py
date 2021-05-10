import csv
import os
import logging
from datetime import datetime, timedelta
from threading import Thread
from common.block import Block
from common.utils import *

class BlockchainReader(Thread):
    def __init__(self, request_queue, result_queue):
        Thread.__init__(self)
        self.request_queue = request_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            request = self.request_queue.get()
            operation = request["operation"]
            if operation == "GET BLOCK":
                logging.info(f"[BLOCKCHAIN_READER] Operation received: {request['operation']}")
                hash_received = request["hash"]
                logging.info(f"[BLOCKCHAIN_READER] Hash received: {request['hash']}")
                client_socket = request["socket"]
                block = self.get_block(hash_received)
                logging.info(f"[BLOCKCHAIN_READER] Block: {block}")
                self.result_queue.put({"socket": client_socket, "result": block.serialize_into_dict()})
            else:
                first_endpoint = request["timestamp"]
                blocks = self.get_blocks_between_minute_interval(first_endpoint) 

    def get_block(self, block_hash):
        hash_file_name = str(block_hash) + '.csv'
        logging.info(f"Hash name: {hash_file_name}")

        if not os.path.exists(hash_file_name):
            logging.info("El archivo no existe")
            return None

        header = {}
        entries = []

        with open(hash_file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                header = {
                    'prev_hash': int(row['prev_hash']), 
                    'nonce': int(row['nonce']),
                    'timestamp': datetime.strptime(row['timestamp'], FULL_DATE_FORMAT),
                    'entries_amount': int(row['entries_amount']),
                    'difficulty': int(row['difficulty'])
                }
                entries = row['entries'].split('-')

        return Block(entries, header)

    def get_blocks_between_minute_interval(self, first_endpoint):
        blocks = []
        second_endpoint = first_endpoint + timedelta(minutes=1)

        day = first_endpoint.strftime(DATE_FORMAT)

        file_name = str(day) + '.csv'

        if not os.path.exists(file_name): 
            return blocks
        with open(file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                timestamp = datetime.strptime(row['timestamp'], FULL_DATE_FORMAT)
                if timestamp >= first_endpoint and timestamp <= second_endpoint:
                    block_hash = int(row['hash'])
                    blocks.append(self.get_block(block_hash))

        return blocks
        