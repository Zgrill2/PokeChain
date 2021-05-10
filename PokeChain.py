import hashlib
import json
from time import time
from block import Block
from hashlib import sha256
import json
import time
import difficulty
from flask import Flask, request
import requests


class Pokechain:

    def __init__(self, chain=[], blockfile_name='chain.json', genesis_phrase="Gotta Catch `em All"):
        self.unconfirmed_transactions = [] # currently unused
        self.chain = chain
        self.blockfile = blockfile_name
        self.genesis_difficulty = 2
        self.genesis_phrase = genesis_phrase
        self.current_difficulty = self.genesis_difficulty
        if len(self.chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, time.time(), self.genesis_phrase, self.genesis_difficulty)
        self.chain.append(genesis_block)
        self.write_chain()

    @property
    def last_block(self):
        rchain = self.chain[-1]
        if isinstance(rchain, dict):
            return Block(rchain["index"], rchain["timestamp"], rchain["previous_hash"], rchain["difficulty"], rchain["nonce"])
        return self.chain[-1]

    def update_chain(self, new_chain):
        self.chain = new_chain
        self.current_difficulty = difficulty.calc_chain_head_difficulty(new_chain)
        self.write_chain()

    def write_chain(self):
        with open(self.blockfile, 'w') as f:
            jchain = {"chain": self.chain}
            jj = str(jchain).replace("'", '"')
            f.write(jj)

    def add_block(self, block):
        """
        A function that adds the block to the chain after verification.
        * Check if difficulty is valid
        * Verify block is valid chain from current HEAD.
        """
        # Check that the stated difficulty is accurate
        if not difficulty.is_valid_difficulty(block, self.chain):
            return False

        if not difficulty.verify_block(block, self.last_block):
            return False

        self.chain.append(block)

        # update our difficulty
        self.current_difficulty = difficulty.calc_chain_head_difficulty(self.chain)

        # don't write every block. it is too often every 100 seems reasonable
        if len(self.chain) % 100 == 0:
            self.write_chain()
        # TODO: File and memory manager to reduce in-memory chain length and maintain an up-to-date filesystem record
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
