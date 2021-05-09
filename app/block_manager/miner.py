import datetime
from common.cryptographic_solver import CryptographicSolver
from threading import Thread
import socket
from sockets.utils import *

# It should have a thread mining and a thread listening whether it needs to stop mining the block

class Miner(Thread):
    def __init__(self, block_queue, stop_queue, result_queue, miner_id, blockchain_host, blockchain_port):
        Thread.__init__(self)
        self.cryptographic_solver = CryptographicSolver()
        self.block_queue = block_queue
        self.stop_queue = stop_queue
        self.result_queue = result_queue
        self.id = miner_id
        self.blockchain_host = blockchain_host
        self.blockchain_port = blockchain_port

    def mine(self, block):
        block.set_timestamp(datetime.datetime.now())
        while not self.cryptographic_solver.solve(block) and not self.stop_queue.empty():
            block.add_nonce()
            block.set_timestamp(datetime.datetime.now())
        
        if not self.stop_queue.empty():
            print(f"Me pidieron que frene y soy el minero {self.id}")
            self.stop_queue.get()
            self.result_queue.put(False)
            return False
        
        self.result_queue.put(True) #TODO: change this
        return True

    def run(self):
        while True:
            block = self.block_queue.get()
            result_mining = self.mine(block)
            if result_mining:
                miner_socket = create_and_connect(self.blockchain_host, self.blockchain_port)
                block_serialized = block.serialize()
                print(f"Quiero mandar el len: {len(block_serialized)}")
                miner_socket.send(number_to_4_bytes(len(block_serialized)))
                # envio el bloque a la blockchain
                # recibo el hash si pudo o la negativa si no pudo
                # escribo el resultado en la cola
                close(miner_socket)
                # send to blockchain
            self.block_queue.task_done()
