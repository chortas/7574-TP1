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
        self._prev_hash = prev_hash
        self._nonce = nonce
        self._timestamp = timestamp
        self._difficulty = difficulty
        self._entries = entries
        self.hash_calculated = hash_received
            
    def compute_hash(self):
        if self.hash_calculated == None:
            header = {
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'entries_amount': len(self.entries),
            'difficulty': self.difficulty
            }
            self.hash_calculated = int(sha256(repr(header).encode('utf-8') + repr(self.entries).encode('utf-8')).hexdigest(), 16)
        return self.hash_calculated

    def __invalidate_calculated_hash(self):
        self.hash_calculated = None

    @property
    def prev_hash(self):
        return self._prev_hash
          
    @prev_hash.setter
    def prev_hash(self, prev_hash):
        self._prev_hash = prev_hash
        self.__invalidate_calculated_hash()

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp
        self.__invalidate_calculated_hash()

    @property
    def nonce(self):
        return self._nonce

    def add_nonce(self):
        self._nonce += 1
        self.__invalidate_calculated_hash()

    @property
    def difficulty(self):
        return self._difficulty
    
    @difficulty.setter
    def difficulty(self, difficulty):
        self._difficulty = difficulty
        self.__invalidate_calculated_hash()
    
    @property
    def entries(self):
        return self._entries

    def get_day(self):
        return self.timestamp.strftime(DATE_FORMAT)

    def serialize_into_dict(self):
        return {'hash': self.compute_hash(), 
                'prev_hash': self.prev_hash, 
                'nonce': self.nonce, 
                'timestamp': str(self.timestamp), 
                'entries_amount': len(self.entries), 
                'difficulty': self.difficulty, 
                'entries': "-".join(self.entries)
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
        entries = "-".join(self.entries)
        return f"""
        'block_hash': {self.compute_hash()}
        
        'header': {{
            'prev_hash':{self.prev_hash}
            'nonce': {self.nonce}
            'timestamp': {self.timestamp}
            'entries_amount': {len(self.entries)}
            'difficulty': {self.difficulty}
        }}
        
        'entries': [
            {entries}
        ]
        """