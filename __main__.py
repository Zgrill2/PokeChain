from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from miner import PokeMiner
from app import app_factory
import math

LISTEN_PORT = 80


if __name__ == '__main__':

    flask_app = app_factory()
    http_server = HTTPServer(WSGIContainer(flask_app), max_body_size=math.inf, max_buffer_size=math.inf)
    http_server.listen(LISTEN_PORT)
    IOLoop.instance().start()


"""
TODO

QoL
Store fellow known nodes to a file for persistence
Add --port option to __main__
add --node option to miner

BUGS:
Fix the no initial json mining bug
        gamer@Di-PC:/mnt/e/programming/f/PokeChain$ sudo python3 miner.py
            Traceback (most recent call last):
              File "miner.py", line 69, in <module>
                m.mine_block()
              File "miner.py", line 21, in mine_block
                new_block = Block(index=last_block.index + 1,
            AttributeError: 'dict' object has no attribute 'index'
Dicts ocasionally getting put onto PokeChain.chain instead of Block objects


Make difficulty dynamic
"""