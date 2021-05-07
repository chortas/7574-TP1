import pytest
from block import Block

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
    