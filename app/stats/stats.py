from queue import Queue
from stats.stats_reader import StatsReader
from stats.stats_writer import StatsWriter
from multiprocessing import Lock

STATS_FILE_NAME = 'stats.csv'

class Stats:
    """Class that wraps concurrency syncronization between read and write processes"""

    def __init__(self, n_miners):
        self.file_lock = Lock()
        self.stats_reader = StatsReader(STATS_FILE_NAME)
        self.stats_writer = StatsWriter(n_miners, STATS_FILE_NAME)

    def read_stats(self):
        '''Reads are done within the main process from each api handler thread'''
        self.file_lock.acquire()
        try:
            return self.stats_reader.read_stats()
        finally:
            self.file_lock.release()

    def write_stat(self, id, stat):
        '''Writes are done within the different miner processes'''
        self.file_lock.acquire()
        try:
            self.stats_writer.add_stat(id, stat)
        finally:
            self.file_lock.release()
            