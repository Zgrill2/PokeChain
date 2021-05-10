import json
import socket
from urllib.parse import urlparse
import os
import requests
from multiprocessing.dummy import Pool
import difficulty
from PokeChain import Pokechain
from block import Block


class PokeNode:
    def __init__(self, app=None, blockchain_file='chain.json', register_initial_node='', port=80):
        self.app = app
        self.blockfile = blockchain_file
        self.port = port
        if not os.path.exists(blockchain_file):
            self.blockchain = Pokechain()
        else:
            with open(self.blockfile) as f:
                data = f.read()
                data = data.replace("'", '"')
                data = json.loads(data)
                self.blockchain = Pokechain(self.file_to_blocks(data))
        self.nodes = set()
        if not register_initial_node == '':
            self.register_node(register_initial_node)

    def init_app(self, app):
        self.app = app

    @property
    def current_difficulty(self):
        return self.blockchain.current_difficulty

    def file_to_blocks(self, jchain={}):
        blocks = []
        for b in jchain['chain']:
            blocks.append(self.create_block(b))
        return blocks

    def create_block(self, bdict):
        try:
            return Block(bdict["index"], bdict["timestamp"], bdict["previous_hash"], bdict["difficulty"], bdict["nonce"])
        except Exception as e:
            print(f'{e}')

    def recieve_block(self, block, sender):
        if not isinstance(block, Block):
            block = self.create_block(block)

        # If the index is lower than our current index, skip validation
        if block.index < self.blockchain.last_block.index:
            return False

        # If block is > our current chain +1, resolve conflicts and skip addition
        # This is the only time we will resolve conflicts
        if block.index > len(self.blockchain.chain):
            self.resolve_conflicts()
            return True

        if self.blockchain.add_block(block):

            print(f'Block added: {block.index} - {block.hash}')


            import concurrent.futures
            import urllib.request
            print(f'{sender}')

            pool = Pool(10)
            futures = []


            d = {'block': json.loads(str(block).replace("'", '"'))}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            for n in self.nodes:
                if n[:n.rindex(':')] == sender:
                    continue
                futures.append(pool.apply_async(requests.post, [f'http://{n}/chain/add'], {'json': d, 'headers': headers, 'timeout': 20}))

            #with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            #    future_to_url = {executor.submit(self.broadcast_new_block, block, node): node for node in self.nodes if not node[:node.rindex(':')] == sender}

        else:
            print(f"New block {block.hash} was invalid: {block}")
            return False
        return True

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        inodes =len(self.nodes)
        parsed_url = urlparse(address)
        #print(f'{parsed_url.netloc}')
        if not parsed_url.netloc == "":
            self.nodes.add(parsed_url.netloc)
        elif len(parsed_url.path) > 0:
            self.nodes.add(parsed_url.path)
        self.resolve_conflicts()
        self.register_back(parsed_url)

    def register_back(self, url):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipaddr = s.getsockname()[0]

        #hostname = socket.gethostname()
        #local_ip = socket.gethostbyname(hostname)
        d = {'nodes': [f'http://{ipaddr}:{self.port}']}
        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.post(f'http://{url.path}/nodes/register', json=d, headers=headers, timeout=20)
        except:
            pass

    def broadcast_new_block(self, block, node):
        d = {'block': json.loads(str(block).replace("'", '"'))}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            response = requests.post(f'http://{node}/chain/add', json=d, headers=headers, timeout=5)
        except Exception as e:
            # note network failure, remove node after X timeouts
            return True
        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.blockchain.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in self.nodes:
            try:
                response = requests.get(f'http://{node}/chain', timeout=5)
            except requests.exceptions.ConnectionError as e:
                print(f'{e}')
                continue
            except requests.exceptions.InvalidURL as e:
                #self.nodes.remove(node)
                continue
            except Exception as e:
                print(f'Uncaught Error: {e}')
                continue

            if response.status_code == 200:

                length = response.json()['length']
                chain = json.loads(response.json()['chain'].replace("'", '"'))

                blocks = []
                for b in chain:
                    blocks.append(Block(b["index"], b["timestamp"], b["previous_hash"], b["difficulty"], b["nonce"]))

                print(f'Comparing our chain: {self.blockchain.last_block.index}-{self.blockchain.last_block.hash}\n'
                      f'         to {blocks[-1].index}-{blocks[-1].hash}')

                # Check if the length is longer and the chain is valid
                if length > max_length and difficulty.validate_chain(blocks):
                    max_length = length
                    new_chain = blocks

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            print(f'Accepted longer chain.')
            self.blockchain.update_chain(new_chain)
            return True

        return False


if __name__ == '__main__':
    pass



