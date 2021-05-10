import hashlib
import json
from time import time
from block import Block
from hashlib import sha256
import json
import time

from flask import Flask, request
import requests


class Pokechain:
    # difficulty of our PoW algorithm
    DESIRED_SECONDS_PER_BLOCK = .51

    def __init__(self, chain=[], blockfile_name='chain.json', genesis_phrase="Gotta Catch `em All"):
        self.unconfirmed_transactions = [] # currently unused
        self.chain = chain
        self.blockfile = blockfile_name
        self.difficulty = 2
        self.genesis_phrase = genesis_phrase
        if len(self.chain) == 0:
            self.create_genesis_block()

    def re_calculate_difficulty(self):
        # Start with initial difficulty
        # playback each difficulty update
        print('re-calculating difficulty')
        difficulty = self.chain[0].difficulty
        for i in range(0, len(self.chain), 50):
            chain = self.chain[0:i]
            difficulty = self.calculate_difficulty(chain, i, difficulty)
        diff = len(self.chain) % 50
        index = len(self.chain) - diff
        self.difficulty = self.calculate_difficulty(self.chain, index, self.difficulty)


    def update_difficulty(self):
        # get past 50 blocks
        # if there isn't 50 blocks, leave
        # calc average time
        # if average < desired, +1 diff, if average > desired -1 diff
        print('updating difficulty')

        diff = len(self.chain) % 50
        index = len(self.chain) - diff
        self.difficulty = self.calculate_difficulty(self.chain, index, self.difficulty)

    def calculate_difficulty(self, chain, index, difficulty):
        # index should be 50, 100, 150, etc
        # chain should be the chain being calculated on
        if index < 50:
            return chain[0].difficulty
        past_50 = chain[index-50:index]
        timestamps = []
        for b in range(len(past_50)-1):
            timestamps.append(past_50[b+1].timestamp - past_50[b].timestamp)
        avg = sum(timestamps) / len(timestamps)
        if avg < Pokechain.DESIRED_SECONDS_PER_BLOCK:
            difficulty += 1
        if avg > Pokechain.DESIRED_SECONDS_PER_BLOCK:
            if difficulty > 0:
                difficulty -= 1
        print(f'difficulty set to {difficulty}. Based on {sum(timestamps) / len(timestamps)}')
        return difficulty

    def is_valid_difficulty(self, block):
        # validates the difficulty in a proposed new block
        chain = self.chain
        index = block.index - (block.index % 50)
        cdifficulty = self.calculate_difficulty(chain, index-1, chain[block.index-1].difficulty)
        t = block.hash[:cdifficulty]
        b = '0' * cdifficulty
        return t == b

    def is_valid_proof(self, block, block_hash):
        """
        Difficulty is currently static.
        When dynamic diff is implemented, diff @ block X will need to be calculated and will be part of verification
        """
        return (block_hash.startswith('0' * block.difficulty) and
                block_hash == block.hash)

    def validate_chain(self, chain):
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
            if not self.is_valid_proof(block, block.hash):
                return False

            if not self.is_valid_difficulty(chain[current_index]):
                return False

            if not current_index == block.index:
                return False

            last_block = block
            current_index += 1

        return True

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, time.time(), self.genesis_phrase, self.difficulty)
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
        self.re_calculate_difficulty()
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

        if not self.is_valid_proof(block, block.hash):
            return False

        if not self.is_valid_difficulty(block):
            return False

        self.chain.append(block)

        # update difficulty every 50 blocks
        if len(self.chain) % 50 == 0:
            self.update_difficulty()

        if len(self.chain) % 100 == 0:
            self.write_chain() # don't write everyblock its too often every 100 seems reasonable
        return True


    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
