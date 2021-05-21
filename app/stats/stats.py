from queue import Queue
from stats.stats_reader import StatsReader
from stats.stats_writer import StatsWriter
from multiprocessing import Lock

class Stats:
    def __init__(self, n_miners):
        self.file_lock = Lock()
        self.stats_reader_queue = Queue()
        self.stats_reader_result_queue = Queue()
        self.stats_reader = StatsReader(self.stats_reader_queue, self.stats_reader_result_queue)
        self.stats_writer = StatsWriter(n_miners)

        self.stats_reader.start()

    def read_stats(self):
        self.stats_reader_queue.put(True)
        return self.stats_reader_result_queue.get()

    def write_stat(self, id, stat):
        self.stats_writer.add_stat(id, stat)
