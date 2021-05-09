#!/usr/bin/env python3
import logging
import os

def parse_config_params():
    config_params = {}
    try:
        config_params["blockchain_ip"] = os.environ["BLOCKCHAIN_IP"]
        config_params["blockchain_port"] = int(os.environ["BLOCKCHAIN_PORT"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting blockchain".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting blockchain".format(e))

    return config_params

def main():
    initialize_log()

    config_params = parse_config_params()

    blockchain_ip = config_params["blockchain_ip"]
    blockchain_port = config_params["blockchain_port"]

    print(f"Blockchain ip: {blockchain_ip}")
    print(f"Blockchain port: {blockchain_port}")

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