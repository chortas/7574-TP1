#!/usr/bin/env python3
import logging
import os
import time
from threading import Lock

from blockchain_manager import BlockchainManager
from blockchain_writer import BlockchainWriter
from query_manager import QueryManager
from common.graceful_stopper import GracefulStopper

def parse_config_params():
    config_params = {}
    try:
        config_params["blockchain_host"] = os.environ["BLOCKCHAIN_HOST"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])
        config_params["blockchain_listeners"] = int(os.environ["BLOCKCHAIN_LISTENERS"])

        config_params["query_host"] = os.environ["QUERY_HOST"]
        config_params["query_port"] = int(os.environ["QUERY_PORT"])
        config_params["query_listeners"] = int(os.environ["QUERY_LISTENERS"])

        config_params["n_readers"] = int(os.environ["N_READERS"])

    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting blockchain".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting blockchain".format(e))

    return config_params

def main():
    initialize_log()

    config_params = parse_config_params()

    blockchain_host = config_params["blockchain_host"]
    blockchain_port = config_params["blockchain_port"]
    blockchain_listeners = config_params["blockchain_listeners"]

    logging.info(f"Blockchain host: {blockchain_host}")
    logging.info(f"Blockchain port: {blockchain_port}")
    logging.info(f"Blockchain listeners: {blockchain_listeners}")

    query_host = config_params["query_host"]
    query_port = config_params["query_port"]
    query_listeners = config_params["query_listeners"]

    logging.info(f"Query host: {query_host}")
    logging.info(f"Query port: {query_port}")
    logging.info(f"Query listeners: {query_listeners}")

    n_readers = config_params["n_readers"]

    block_index_lock = Lock()
    block_lock = Lock()

    graceful_stopper = GracefulStopper()
    blockchain_writer = BlockchainWriter(block_index_lock, block_lock)

    blockchain_manager = BlockchainManager(blockchain_host, blockchain_port, blockchain_listeners, 
    blockchain_writer, graceful_stopper)
    query_manager = QueryManager(query_host, query_port, query_listeners, n_readers, 
    block_index_lock, block_lock, graceful_stopper)

    blockchain_manager.start()
    query_manager.start()

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