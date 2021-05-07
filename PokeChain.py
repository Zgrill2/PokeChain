import hashlib
import json
from time import time
from block import Block
from hashlib import sha256
import json
import time

from flask import Flask, request
import requests


def validate_chain(chain):
    """
    Determine if a given blockchain is valid
    :param chain: <list> A blockchain
    :return: <bool> True if valid, False if not
    """
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
        block = chain[current_index]

        # Check that the hash of the block is correct
        if block.previous_hash != last_block.hash:
            return False

        # Check that the Proof of Work is correct
        if not is_valid_proof(block, block.hash):
            return False

        last_block = block
        current_index += 1

    return True


def is_valid_proof(block, block_hash):
    """
    Difficulty is currently static.
    When dynamic diff is implemented, diff @ block X will need to be calculated and will be part of verification
    """
    return (block_hash.startswith('0' * Pokechain.difficulty) and
            block_hash == block.hash)


class Pokechain:
    # difficulty of our PoW algorithm
    difficulty = 4

    def __init__(self, chain=[], blockfile_name='chain.json', genesis_phrase="Gotta Catch `em All"):
        self.unconfirmed_transactions = [] # currently unused
        self.chain = chain
        self.blockfile = blockfile_name
        self.genesis_phrase = genesis_phrase
        if len(self.chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, time.time(), self.genesis_phrase)
        self.chain.append(genesis_block)
        self.write_chain()

    @property
    def last_block(self):
        rchain = self.chain[-1]
        if isinstance(rchain, dict):
            return Block(rchain["index"], rchain["timestamp"], rchain["previous_hash"], rchain["nonce"])
        return self.chain[-1]

    def update_chain(self, new_chain):
        self.chain = new_chain
        self.write_chain()

    def write_chain(self):
        with open(self.blockfile, 'w') as f:
            jchain = {"chain": self.chain}
            jj = str(jchain).replace("'", '"')
            f.write(jj)

    def add_block(self, block):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not is_valid_proof(block, block.hash):
            return False

        self.chain.append(block)
        self.write_chain()
        return True


    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
