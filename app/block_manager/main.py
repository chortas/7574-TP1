#!/usr/bin/env python3
import logging
import os
from block import Block
from block_manager import BlockManager

def parse_config_params():
    config_params = {}
    try:
        config_params["n_miners"] = int(os.environ["N_MINERS"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    initialize_log()

    config_params = parse_config_params()
    block_manager = BlockManager(config_params["n_miners"])
    block = Block([])
    block_manager.send_block(block)
    other_block = Block([])
    block_manager.send_block(other_block)

    block_manager.join()

def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__== "__main__":
    main()