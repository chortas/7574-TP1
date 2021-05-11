from datetime import datetime
import logging

TARGET_TIME_IN_SECONDS = 12 
BLOCKS_PROCESSED_TO_ADJUST_DIFFICULTY = 256

class DifficultyAdjuster:
    """Class that adjusts difficulty given amount of blocks sent"""
    def __init__(self):
        self.difficulty = 1
        self.blocks_processed = 0    
        self.start_time = datetime.now()

    def add_block_to_count(self):
        self.blocks_processed += 1
        if self.blocks_processed >= BLOCKS_PROCESSED_TO_ADJUST_DIFFICULTY:
            logging.info("[DIFFICULTY_ADJUSTER] Difficulty is being adjusted...")
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            self.difficulty = self.__adjust_difficulty(self.difficulty, elapsed_time, TARGET_TIME_IN_SECONDS, self.blocks_processed)
            self.blocks_processed = 0
            self.start_time = datetime.now()

    def get_difficulty(self):
        return self.difficulty

    def __adjust_difficulty(self, prev_difficulty, elapsed_time, target_time, blocks_processed):
        return prev_difficulty * (blocks_processed/elapsed_time) * target_time
