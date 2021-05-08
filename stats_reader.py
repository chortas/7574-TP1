import csv

class StatsReader:
    def get_stats(self):
          with open('stats.csv', 'r') as stats_file_reader:
                csv_reader = csv.DictReader(stats_file_reader)
                return list(csv_reader)
