import csv
import os
import logging
from datetime import datetime, timedelta
from threading import Thread

from common.block import Block
from common.utils import *

class BlockchainReader(Thread):
    """Class that manages the readings from the blockchain, specially obtaining a
    block given a hash and blocks given a period of time of 1 minute"""

    def __init__(self, request_queue, result_queue):
        Thread.__init__(self)
        self.request_queue = request_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            request = self.request_queue.get()
            operation = request["operation"]
            logging.info(f"[BLOCKCHAIN_READER] Operation received: {operation}")
            
            if operation == GET_BLOCK_BY_HASH_OP:
                hash_received = request["hash"]
                client_socket = request["socket"]
                block = self.__get_block(hash_received)
                serialized_block = block.serialize_into_dict() if block != None else {}
                self.result_queue.put({"socket": client_socket, "result": serialized_block})
            else:
                first_endpoint = request["timestamp"]
                client_socket = request["socket"]
                blocks = self.__get_blocks_between_minute_interval(first_endpoint)
                serialized_blocks = [block.serialize_into_dict() for block in blocks]
                self.result_queue.put({"socket": client_socket, "result": serialized_blocks})
      
    def __get_block(self, block_hash):
        hash_file_name = str(block_hash) + '.csv'

        if not os.path.exists(hash_file_name):
            logging.info("[BLOCKCHAIN_READER] The file doesn't exist")
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

    def __get_blocks_between_minute_interval(self, first_endpoint):
        try:
            first_endpoint = datetime.strptime(first_endpoint, MINUTE_FORMAT)
        except ValueError:
            logging.info("[BLOCKCHAIN_READER] The date is not valid or it should not contain seconds")
            return []

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
                if first_endpoint <= timestamp <= second_endpoint:
                    block_hash = int(row['hash'])
                    blocks.append(self.__get_block(block_hash))

        return blocks
        