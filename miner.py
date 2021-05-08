import json
import time
import requests

from block import Block
from node import PokeNode



keys = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "a": "z",
    "b": "x",
    #    "l": "q",
    #w    "r": "e",
    "start": "g",
    "select": "t"
}

k = [kk for kk in keys.keys()]

moves_mining_for = ["a", "b", "left", "right", "up", "down"]


class PokeMiner:
    def __init__(self, master_node=''):
        self.node = PokeNode()
        self.master_node = master_node # to provide miners an actual network node to use

    def mine_block(self):
        while True:
            last_block = self.get_last_block()
            new_block = Block(index=last_block.index + 1,
                              timestamp=time.time(),
                              previous_hash=last_block.hash,
                              difficulty=self.node.blockchain.difficulty)

            result = self.proof_of_work(new_block)
            if not result:
                continue

            character = new_block.hash[-1]
            result = ord(character) % len(k)
            if k[result] in moves_mining_for:
                self.emit_block(new_block)


    def get_last_block(self):
        """
        try:
            response = requests.get(f'{self.master_node}/chain/last')
        except Exception as e:
            print(f'Your node may be down. Success not guarenteed.')
            return False
        sblock = '{"block" : ' + response.json()["block"] + '}'
        lblock = json.loads(sblock.replace("'", '"'))['block'] # am I dumb or is this .replace the stupidest thing ever

        if not isinstance(lblock, Block):
            lblock = self.node.create_block(lblock)

        if lblock.index > len(self.node.blockchain.chain):
            self.update_mining_chain()

        return lblock"""
        return self.node.blockchain.last_block

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.hash
        # TODO: implement dynamic difficulty
        while not computed_hash.startswith('0' * self.node.blockchain.difficulty):
            # Leave if our last_block is outdated
            b = self.get_last_block()
            if b.index >= block.index:
                return False
            block.nonce += 1
            computed_hash = block.hash
            if block.nonce % 1000000 == 0:
                print(f'Attempted {block.nonce} tries to mine block {len(self.node.blockchain.chain)}')
        return True


    def update_mining_chain(self):
        try:
            response = requests.get(f'{self.master_node}/chain')
        except Exception as e:
            print(f'{e}')
            return False, 'Your server seems to be offline'
        chain = response.json()
        jchain = '{ "chain" : '+ chain['chain'] + "}"
        jchain = json.loads(jchain.replace("'", '"'))
        self.node.blockchain.update_chain(self.node.file_to_blocks(jchain))
        return True, 'You are now at HEAD of server'

    def emit_block(self, block):

        d = {'block': json.loads(str(block).replace("'", '"'))}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            response = requests.post(f'{self.master_node}/chain/add', json=d, headers=headers)
        except Exception as e:
            return False, 'Your server seems to be offline'
        print(f'{response.json()["message"]}')
        self.update_mining_chain()

    def set_master_node(self, hostname):
        self.master_node = hostname
        self.node.register_node(hostname)
        self.update_mining_chain()


if __name__ == '__main__':
    m = PokeMiner()
    m.set_master_node('http://192.168.1.117:5000')
    m.mine_block()