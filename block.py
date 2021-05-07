import json
from hashlib import sha256


class Block:
    def __init__(self, index, timestamp, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    @property
    def hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__str__(), sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def __str__(self):
        return str({
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce
        })

    def __repr__(self):
        return str({
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce
        })

    def __dict__(self):
        return {
            "index": self.index, "timestamp": self.timestamp, "previous_hash": self.previous_hash, "nonce": self.nonce
        }