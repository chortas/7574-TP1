import csv

class StatsWriter:

    def __init__(self, n_miners):
        self.file_name = 'stats.csv'
        self.fieldnames = ['id_miner', 'n_succeeded', 'n_failed']
        with open(self.file_name, mode='w') as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=self.fieldnames)
            writer.writeheader()
            
            for id_miner in range(n_miners):
                writer.writerow({'id_miner': id_miner, 'n_succeeded': 0, "n_failed": 0})
    
    def add_stat(self, id_miner, is_succeeded):
        data = []

        with open(self.file_name, 'r') as stats_file_reader:
            reader = csv.reader(stats_file_reader)
            rows = list(reader)[1:]

        with open(self.file_name, 'w') as stats_file_writer:
            writer = csv.DictWriter(stats_file_writer, fieldnames=self.fieldnames)
            writer.writeheader()
            
            for row in rows:
                id_miner_row, n_succeeded, n_failed = int(row[0]), int(row[1]), int(row[2])

                if id_miner == id_miner_row and is_succeeded:
                    n_succeeded += 1
                
                if id_miner == id_miner_row and not is_succeeded:
                    n_failed += 1
               
                writer.writerow({'id_miner': id_miner_row, 
                                'n_succeeded': n_succeeded, 
                                'n_failed': n_failed})
        