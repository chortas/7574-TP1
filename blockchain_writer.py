import csv

class BlockchainWriter:
    def write_block(self, block):
        # file with hash and all information from block
        file_name = str(block.hash()) + '.csv'
    
        with open(file_name, mode='w') as block_file:

            fieldnames = ['hash', 'prev_hash', 'nonce', 'timestamp', 'entries_amount', 'difficulty', 'entries']
            writer = csv.DictWriter(block_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({'hash': block.hash(), 
                            'prev_hash': block.get_prev_hash(), 
                            'nonce': block.get_nonce(), 
                            'timestamp': block.get_timestamp(), 
                            'entries_amount': block.get_entries_amount(), 
                            'difficulty': block.get_difficulty(), 
                            'entries': block.get_entries()
                            })

        # do with timestamp