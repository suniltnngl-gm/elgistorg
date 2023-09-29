import hashlib
import random
import socket
from collections import OrderedDict

class Block:
    def __init__(self, previous_hash, transaction_data, nonce=0):
        self.previous_hash = previous_hash
        self.transaction_data = transaction_data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = str(self.previous_hash) + str(self.transaction_data) + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = OrderedDict()
        self.genesis_block = Block("0", [])
        self.chain[self.genesis_block.hash] = self.genesis_block
        self.nodes = []

    def add_block(self, block):
        self.chain[block.hash] = block

    def is_valid_block(self, block):
        previous_block = self.chain[block.previous_hash]
        if block.previous_hash != previous_block.hash:
            return False
        if not self.is_valid_transaction_data(block.transaction_data):
            return False
        return True

    def is_valid_transaction_data(self, transaction_data):
        # TODO: Implement this method to validate the transaction data.
        return True

    def proof_of_work(self, block):
        while True:
            block.nonce += 1
            hash = block.calculate_hash()
            if hash.startswith('0000'):
                break
        return hash

    def connect_to_node(self, node):
        self.nodes.append(node)

    def broadcast_block(self, block):
        for node in self.nodes:
            node.add_block(block)

class Node:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 5000))
        self.socket.listen(1)

    def listen_for_blocks(self):
        while True:
            connection, address = self.socket.accept()
            data = connection.recv(1024)
            block = Block.from_json(data)
            self.blockchain.add_block(block)
            connection.close()

    def broadcast_block(self, block):
        for node in self.blockchain.nodes:
            node.socket.sendall(block.to_json().encode())

if __name__ == "__main__":
    blockchain = Blockchain()
    node = Node(blockchain)
    node.listen_for_blocks()

    while True:
        transaction_data = input("Enter a transaction: ")
        block = Block(blockchain.chain[-1].hash, transaction_data)
        hash = blockchain.proof_of_work(block)
        block.hash = hash
        blockchain.add_block(block)
        node.broadcast_block(block)
