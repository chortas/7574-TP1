import pytest
from datetime import datetime
from common.block import Block

class TestBlock:
    def test_prev_hash(self):
        block = Block([])
        some_hash = "someHash"
        block.prev_hash = some_hash
        assert block.prev_hash == some_hash

    def test_right_number_chunk(self):
        entries = [1 for i in range(257)]
        with pytest.raises(ValueError, match='Exceeding chunk size'):
            block = Block(entries)
    
    def test_get_right_day(self):
        block = Block([])
        timestamp = datetime(2020, 5, 17, 22, 30)
        block.timestamp = timestamp
        assert block.get_day() == '2020-05-17'

