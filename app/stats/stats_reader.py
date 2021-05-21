import csv

class StatsReader():
    """Class that reads stats file to provide stats"""
    def __init__(self, file_name):
        self.file_name = file_name
    
    def read_stats(self):
        with open(self.file_name, 'r') as stats_file_reader:
            csv_reader = csv.DictReader(stats_file_reader)
            return list(csv_reader)
    