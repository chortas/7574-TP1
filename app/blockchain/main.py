#!/usr/bin/env python3
import logging
import os
from blockchain_manager import BlockchainManager

def parse_config_params():
    config_params = {}
    try:
        config_params["blockchain_host"] = os.environ["BLOCKCHAIN_HOST"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])
        config_params["blockchain_listeners"] = int(os.environ["BLOCKCHAIN_LISTENERS"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting blockchain".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting blockchain".format(e))

    return config_params

def main():
    initialize_log()
    print("Hola")

    config_params = parse_config_params()

    blockchain_host = config_params["blockchain_host"]
    blockchain_port = config_params["blockchain_port"]
    blockchain_listeners = config_params["blockchain_listeners"] #TODO: see if this will be used

    print(f"Blockchain host: {blockchain_host}")
    print(f"Blockchain port: {blockchain_port}")
    print(f"Blockchain listeners: {blockchain_listeners}")

    blockchain_manager = BlockchainManager(blockchain_host, blockchain_port)

    blockchain_manager.receive_blocks()

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