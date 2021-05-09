from hashlib import sha256
from datetime import datetime
from common.utils import *
import json

MAX_ENTRIES_AMOUNT = 256

class Block: 
    def __init__(self, entries, header={}):
        if header != {}:
            self.header = header
        else:
            self.header = {
                'prev_hash': 0,
                'nonce': 0,
                'timestamp': get_and_format_datetime_now(),
                'entries_amount': len(entries),
                'difficulty': 1
            }
        if (len(entries) > MAX_ENTRIES_AMOUNT):
            raise ValueError("Exceeding chunk size")
        
        self.entries = entries
            
    def hash(self):
        return int(sha256(repr(self.header).encode('utf-8') + repr(self.entries).encode('utf-8')).hexdigest(), 16)
        
    def set_prev_hash(self, prev_hash):
        self.header['prev_hash'] = prev_hash

    def set_timestamp(self, timestamp):
        self.header['timestamp'] = timestamp

    def add_nonce(self):
        self.header['nonce'] += 1

    def get_difficulty(self):
        return self.header['difficulty']

    def get_prev_hash(self):
        return self.header['prev_hash']
    
    def get_nonce(self):
        return self.header['nonce']
    
    def get_timestamp(self):
        return self.header['timestamp']
    
    def get_entries_amount(self):
        return self.header['entries_amount'] 
    
    def get_entries(self):
        return self.entries
    
    def get_day(self):
        return self.header['timestamp'].strftime(DATE_FORMAT)

    def add_entry(self, entry):
        self.entries.append(entry)
        self.header['entries_amount'] += 1

    def serialize_into_dict(self):
        return {'hash': self.hash(), 
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
        header = {
                    'prev_hash': int(json_data['prev_hash']), 
                    'nonce': int(json_data['nonce']),
                    'timestamp': datetime.strptime(json_data['timestamp'], FULL_DATE_FORMAT),
                    'entries_amount': int(json_data['entries_amount']),
                    'difficulty': int(json_data['difficulty'])
                }
        entries = json_data['entries'].split('-')
        return cls(entries, header=header)

    def __str__(self):
        entries = ",".join(self.entries)
        return f"""
        'block_hash': {self.hash()}
        
        'header': {{
            'prev_hash':{self.header['prev_hash']}
            'nonce': {self.header['nonce']}
            'timestamp': {self.header['timestamp']}
            'entries_amount': {self.header['entries_amount']}
            'difficulty': {self.header['difficulty']}
        }}
        
        'entries': [
            {entries}
        ]
        """