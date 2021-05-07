import json
import time

import requests

from block import Block
from node import PokeNode


class PokeMiner:
    def __init__(self, master_node=''):
        self.node = PokeNode()
        self.master_node = master_node # to provide miners an actual network node to use

    def mine_block(self):
        last_block = self.node.blockchain.last_block

        if not isinstance(last_block, Block):
            last_block = self.node.create_block(last_block)
        new_block = Block(index=last_block.index + 1,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        self.proof_of_work(new_block)
        self.node.add_block(new_block)

        return new_block.index

    def set_master_node(self, hostname):
        """
        try:
            response = requests.get(f'{hostname}/chain')
            chain = json.loads(response.json()['chain'].replace("'", '"'))

            blocks = []
            for b in chain:
                blocks.append(Block(b["index"], b["timestamp"], b["previous_hash"], b["nonce"]))
            self.nodeblockchain.update_chain(blocks)
            print(f'Loaded chain from master node: {len(self.nodeblockchain.chain)} blocks')
        except requests.exceptions.ConnectionError as e:
            print(f'OOF: {e}')
            return False
        """
        self.master_node = hostname
        self.node.register_node(hostname)
        try:
            response = requests.get(f'{hostname}/chain')
        except Exception as e:
            print(f'{e}')
            return False, 'Your server seems to be offline'
        chain = response.json()

        jchain = '{ "chain" : '+ chain['chain'] + "}"
        jchain = json.loads(jchain.replace("'", '"'))
        self.node.blockchain.update_chain(self.node.file_to_blocks(jchain))

    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.hash
        # TODO: implement dynamic difficulty
        while not computed_hash.startswith('0' * self.node.current_difficulty):
            # update our block if the chain has moved on
            try:
                if self.node.blockchain.last_block.index > block.index:
                    block.index = self.node.blockchain.last_block
                    block.timestamp = time.time()
                    block.previous_hash = self.node.blockchain.last_block.hash
            except Exception as e:
                print(f'{self.node.blockchain.last_block.index}\n{block.index}')
            block.nonce += 1
            computed_hash = block.hash
            if block.nonce % 1000000 == 0:
                print(f'Attempted {block.nonce} tries to mine block {len(self.node.blockchain.chain)}')
            elif block.nonce % 999999 == 0:
                try:
                    response = requests.get(f'{self.master_node}/chain')
                except Exception as e:
                    print(f'Your node may be down. Success not guarenteed.')
                    continue
                clength = response.json()['length']
                if clength > len(self.node.blockchain.chain):
                    self.node.resolve_conflicts()


if __name__ == '__main__':
    m = PokeMiner()
    m.set_master_node('http://192.168.1.153:80')
    while True:
        m.mine_block()
