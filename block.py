from hashlib import sha256

MAX_ENTRIES_AMOUNT = 256

class Block: 
    def __init__(self, entries):
        self.header = {
            'prev_hash': 0,
            'nonce': 0,
            'timestamp': None,
            'entries_amount': len(entries),
            'difficulty': 1
        }
        if (len(entries) > MAX_ENTRIES_AMOUNT):
            raise 'Exceeding max block size'
        
        self.entries = entries
            
    def hash(self):
        return int(sha256(repr(self.header).encode('utf-8') + repr(self.entries).encode('utf-8')).hexdigest(), 16)
        
    def set_prev_hash(prev_hash):
        self.header['prev_hash'] = prev_hash

    def set_timestamp(timestamp):
        self.header['timestamp'] = timestamp

    def add_nonce():
        self.header['nonce'] += 1

    def get_difficulty():
        return self.header['difficulty']
        
    def __str__(self):
        entries = ",".join(self.entries)
        return f"""
        'block_hash': {hex(self.hash())}
        
        'header': {{
            'prev_hash':{hex(self.header['prev_hash'])}
            'nonce': {self.header['nonce']}
            'timestamp': {self.header['timestamp']}
            'entries_amount': {self.header['entries_amount']}
            'difficulty': {self.header['difficulty']}
        }}
        
        'entries': [
            {entries}
        ]
        """