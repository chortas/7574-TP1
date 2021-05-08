import pytest
from datetime import datetime
from common.block import Block

class TestBlock:
    def test_prev_hash(self):
        block = Block([])
        some_hash = "someHash"
        block.set_prev_hash(some_hash)
        assert block.get_prev_hash() == some_hash

    def test_right_number_chunk(self):
        entries = [1 for i in range(257)]
        with pytest.raises(ValueError, match='Exceeding chunk size'):
            block = Block(entries)
    
    def test_get_right_day(self):
        block = Block([])
        timestamp = datetime(2020, 5, 17, 22, 30)
        block.set_timestamp(timestamp)
        assert block.get_day() == '05-17-2020'

    def test_add_entry(self):
        block = Block([])
        assert block.get_entries() == []
        block.add_entry('entry')
        assert block.get_entries() == ['entry']
        assert block.get_entries_amount() == 1
