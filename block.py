import json
from hashlib import sha256


class Block:
    def __init__(self, index, timestamp, previous_hash, difficulty, nonce=0, name=''):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.name = name
        self.difficulty = difficulty

    def is_valid_proof(self, block_hash):
        """
        Potentially vestigial function
        """
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == self.hash)

    @property
    def hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__str__(), sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def __str__(self):
        return str({
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce, "difficulty": self.difficulty
        })

    def __repr__(self):
        return str({
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce, "difficulty": self.difficulty
        })

    def __dict__(self):
        return {
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce, "difficulty": self.difficulty
        }