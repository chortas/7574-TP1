#!/usr/bin/env python3
import logging
import os
from common.block import Block
from block_manager import BlockManager

def parse_config_params():
    config_params = {}
    try:
        config_params["n_miners"] = int(os.environ["N_MINERS"])
        config_params["blockchain_host"] = os.environ["BLOCKCHAIN_HOST"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting block manager".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting block manager".format(e))

    return config_params

def main():
    initialize_log()

    config_params = parse_config_params()

    n_miners = config_params["n_miners"]
    blockchain_host = config_params["blockchain_host"]
    blockchain_port = config_params["blockchain_port"]

    block_manager = BlockManager(n_miners, blockchain_host, blockchain_port)
    
    block = Block([])
    block_manager.send_block(block)

    block_2 = Block([])
    block_manager.send_block(block_2)

    block_3 = Block([])
    block_manager.send_block(block_3)

    #block_manager.join()

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