import pytest
import csv
import os
from stats.stats_writer import StatsWriter

class TestStatsWriter:

    def setup_method(self, method):
        self.stats_writer = StatsWriter(3)
        
    def teardown_method(self):
        os.remove('stats.csv')

    def test_initialize_ok(self):
        with open('stats.csv', 'r') as stats_file_reader:
            csv_reader = csv.DictReader(stats_file_reader)
            line_count = 0

            for row in csv_reader:
                if line_count == 0:
                    assert row['id_miner'] == '0'
                elif line_count == 1:
                    assert row['id_miner'] == '1'
                else:
                    assert row['id_miner'] == '2'

                assert row['n_succeeded'] == '0'
                assert row['n_failed'] == '0'

                line_count += 1

    def test_add_succeeded_ok(self):
        self.stats_writer.add_stat(0, True)
        self.stats_writer.add_stat(0, True)

        with open('stats.csv', 'r') as stats_file_reader:
            csv_reader = csv.DictReader(stats_file_reader)
            line_count = 0

            for row in csv_reader:
                if line_count == 0:
                    assert row['id_miner'] == '0'
                    assert row['n_succeeded'] == '2'
                elif line_count == 1:
                    assert row['id_miner'] == '1'
                    assert row['n_succeeded'] == '0'
                else:
                    assert row['id_miner'] == '2'
                    assert row['n_succeeded'] == '0'

                assert row['n_failed'] == '0'

                line_count += 1

    def test_add_failed_ok(self):
        self.stats_writer.add_stat(0, False)

        with open('stats.csv', 'r') as stats_file_reader:
            csv_reader = csv.DictReader(stats_file_reader)
            line_count = 0

            for row in csv_reader:
                if line_count == 0:
                    assert row['id_miner'] == '0'
                    assert row['n_failed'] == '1'
                elif line_count == 1:
                    assert row['id_miner'] == '1'
                    assert row['n_failed'] == '0'
                else:
                    assert row['id_miner'] == '2'
                    assert row['n_failed'] == '0'

                assert row['n_succeeded'] == '0'

                line_count += 1
    
    def test_add_failed_and_succeeded_ok(self):
        self.stats_writer.add_stat(0, False)
        self.stats_writer.add_stat(1, True)

        with open('stats.csv', 'r') as stats_file_reader:
            csv_reader = csv.DictReader(stats_file_reader)
            line_count = 0

            for row in csv_reader:
                if line_count == 0:
                    assert row['id_miner'] == '0'
                    assert row['n_failed'] == '1'
                    assert row['n_succeeded'] == '0'
                elif line_count == 1:
                    assert row['id_miner'] == '1'
                    assert row['n_failed'] == '0'
                    assert row['n_succeeded'] == '1'
                else:
                    assert row['id_miner'] == '2'
                    assert row['n_failed'] == '0'
                    assert row['n_succeeded'] == '0'

                line_count += 1
                