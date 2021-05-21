import csv
from threading import Thread

class StatsReader(Thread):
    """Class that reads stats file to provide stats"""
    
    def __init__(self, stats_queue, result_queue):
        Thread.__init__(self)
        self.stats_queue = stats_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            self.stats_queue.get() 
            with open('stats.csv', 'r') as stats_file_reader:
                csv_reader = csv.DictReader(stats_file_reader)
                self.result_queue.put(list(csv_reader))
    