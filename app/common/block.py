import json
import logging
from hashlib import sha256
from datetime import datetime

from common.utils import *

MAX_ENTRIES_AMOUNT = 256

class Block: 
    """Representation of a block"""
    
    def __init__(self, entries, prev_hash=0, nonce=0, timestamp=get_and_format_datetime_now(),
    difficulty=1, hash_received=0):

        if (len(entries) > MAX_ENTRIES_AMOUNT):
            raise ValueError("Exceeding chunk size")
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.entries_amount = len(entries)
        self.difficulty = difficulty
        self.entries = entries
        self.hash_calculated = hash_received
            
    def compute_hash(self):
        if self.hash_calculated == None:
            logging.info("Calculating hash...")
            header = {
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'entries_amount': self.entries_amount,
            'difficulty': self.difficulty
            }
            self.hash_calculated = int(sha256(repr(header).encode('utf-8') + repr(self.entries).encode('utf-8')).hexdigest(), 16)
        else:
            logging.info("Not calculating hash!")
        return self.hash_calculated

    def __invalidate_calculated_hash(fn):
        def wrapper(self, *args, **kwargs):
            self.hash_calculated = None
            fn(self, *args, **kwargs)
        return wrapper

    @__invalidate_calculated_hash
    def set_prev_hash(self, prev_hash):
        self.prev_hash = prev_hash

    @__invalidate_calculated_hash
    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    @__invalidate_calculated_hash
    def add_nonce(self):
        self.nonce += 1
    
    @__invalidate_calculated_hash
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def get_difficulty(self):
        return self.difficulty

    def get_prev_hash(self):
        return self.prev_hash
    
    def get_nonce(self):
        return self.nonce
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_entries_amount(self):
        return self.entries_amount
    
    def get_entries(self):
        return self.entries
    
    def get_day(self):
        return self.timestamp.strftime(DATE_FORMAT)

    def serialize_into_dict(self):
        return {'hash': self.compute_hash(), 
                'prev_hash': self.get_prev_hash(), 
                'nonce': self.get_nonce(), 
                'timestamp': str(self.get_timestamp()), 
                'entries_amount': self.get_entries_amount(), 
                'difficulty': self.get_difficulty(), 
                'entries': "-".join(self.get_entries())
                }

    def serialize(self):
        return json.dumps(self.serialize_into_dict())
    
    @classmethod
    def deserialize(cls, json_to_deserialize):
        json_data = json.loads(json_to_deserialize)
        prev_hash = int(json_data['prev_hash'])
        nonce = int(json_data['nonce'])
        timestamp = datetime.strptime(json_data['timestamp'], FULL_DATE_FORMAT)
        difficulty = int(json_data['difficulty'])
        entries = tuple(json_data['entries'].split('-'))
        hash_received = int(json_data['hash'])
        return cls(entries, prev_hash=prev_hash, nonce=nonce, timestamp=timestamp, difficulty=difficulty,
        hash_received=hash_received)

    def __str__(self):
        entries = ",".join(self.entries)
        return f"""
        'block_hash': {self.compute_hash()}
        
        'header': {{
            'prev_hash':{self.prev_hash}
            'nonce': {self.nonce}
            'timestamp': {self.timestamp}
            'entries_amount': {self.entries_amount}
            'difficulty': {self.difficulty}
        }}
        
        'entries': [
            {entries}
        ]
        """