import pytest
from stats.stats_reader import StatsReader
from stats.stats_writer import StatsWriter

class TestStatsReader:
    def test_stats_ok(self):
        stats_reader = StatsReader()
        stats_writer = StatsWriter(3)
        
        stats = stats_reader.get_stats()

        line_count = 0
        for stat in stats:
            if line_count == 0:
                assert stat['id_miner'] == '0'
            elif line_count == 1:
                assert stat['id_miner'] == '1'
            else:
                assert stat['id_miner'] == '2'

            assert stat['n_succeeded'] == '0'
            assert stat['n_failed'] == '0'

            line_count += 1
            