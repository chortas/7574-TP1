#!/usr/bin/env python3
import logging
import os
from queue import Queue
from common.block import Block
from miner_manager import MinerManager
from block_builder import BlockBuilder
from api.api_handler import ApiHandler

def parse_config_params():
    config_params = {}
    try:
        config_params["n_miners"] = int(os.environ["N_MINERS"])
        config_params["blockchain_host"] = os.environ["BLOCKCHAIN_HOST"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])

        config_params["api_port"] = int(os.environ["API_PORT"])
        config_params["api_listeners"] = int(os.environ["API_LISTENERS"])
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

    api_port = config_params["api_port"]
    api_listeners = config_params["api_listeners"]

    logging.info(f"Api port: {api_port}")
    logging.info(f"Api listeners: {api_listeners}")

    miner_manager = MinerManager(n_miners, blockchain_host, blockchain_port, Queue())
    api_handler = ApiHandler(api_port, api_listeners, miner_manager)
    api_handler.run()

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