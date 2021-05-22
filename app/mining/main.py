#!/usr/bin/env python3
import logging
import os
from queue import Queue
from multiprocessing import Lock

from miner_manager import MinerManager
from api.api_handler import ApiHandler
from stats.stats import Stats
from common.graceful_stopper import GracefulStopper

def parse_config_params():
    config_params = {}
    try:
        config_params["n_miners"] = int(os.environ["N_MINERS"])

        config_params["blockchain_host"] = os.environ["BLOCKCHAIN_HOST"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])

        config_params["api_port"] = int(os.environ["API_PORT"])
        config_params["api_listeners"] = int(os.environ["API_LISTENERS"])

        config_params["query_host"] = os.environ["QUERY_HOST"]
        config_params["query_port"] = int(os.environ["QUERY_PORT"])

        config_params["timeout_chunk"] = int(os.environ["TIMEOUT_CHUNK"])
        config_params["limit_chunk"] = int(os.environ["LIMIT_CHUNK"])

        config_params["n_clients"] = int(os.environ["N_CLIENTS"])

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

    query_host = config_params["query_host"]
    query_port = config_params["query_port"]

    timeout_chunk = config_params["timeout_chunk"]
    limit_chunk = config_params["limit_chunk"]

    n_clients = config_params["n_clients"]

    stats = Stats(n_miners)
    block_queue = Queue()
    graceful_stopper = GracefulStopper()

    miner_manager = MinerManager(n_miners, blockchain_host, blockchain_port, block_queue, stats, 
    graceful_stopper)
    api_handler = ApiHandler(api_port, api_listeners, block_queue, query_host, query_port, 
    timeout_chunk, limit_chunk, n_clients, stats, graceful_stopper)

    miner_manager.start()
    api_handler.start()
    
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