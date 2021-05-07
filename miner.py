import json
import time

import requests
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from app import app_factory
from block import Block
from node import PokeNode


class PokeMiner:
    def __init__(self, master_node=''):
        self.node = PokeNode()
        self.master_node = master_node # to provide miners an actual network node to use

    async def mine_block(self):
        while True:
            last_block = self.get_last_block()
            new_block = Block(index=last_block.index + 1,
                              timestamp=time.time(),
                              previous_hash=last_block.hash)

            if not self.proof_of_work(new_block):
                return False
            self.emit_block(new_block)
            #self.node.add_block(new_block)


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
        while not computed_hash.startswith('0' * self.node.current_difficulty):
            # Leave if our last_block is outdated
            b = self.get_last_block()
            if b.index >= block.index:
                return False
            block.nonce += 1
            computed_hash = block.hash
            if block.nonce % 1000000 == 0:
                print(f'Attempted {block.nonce} tries to mine block {len(self.node.blockchain.chain)}')
            #elif block.nonce % 999999 == 0:


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

        #if self.blockchain.add_block(block):
        print(f'Block added')
        d = {'block': json.loads(str(block).replace("'", '"'))}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            response = requests.post(f'{self.master_node}/chain/add', json=d, headers=headers)
        except Exception as e:
            return False, 'Your server seems to be offline'
        re = response.json()
        print(f'{response.json()["message"]}')
        if re['validation'] == False:
            self.update_mining_chain()

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
        self.update_mining_chain()


LISTEN_PORT = 5000

import math

if __name__ == '__main__':
    m = PokeMiner()
    m.set_master_node('http://192.168.1.153:80')
    m.mine_block()
    flask_app = app_factory()
    http_server = HTTPServer(WSGIContainer(flask_app), max_body_size=math.inf, max_buffer_size=math.inf)
    http_server.listen(LISTEN_PORT)
    IOLoop.instance().start()
