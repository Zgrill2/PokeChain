import json

import pyautogui
import requests
import string

def press_key(key, n = 1):
    for _ in range(n):
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)


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

current_block = 1
blockchain = []

from block import Block


def create_block(bdict):
    return Block(bdict["index"], bdict["timestamp"], bdict["previous_hash"], bdict["nonce"])


def get_current_chain():
    try:
        response = requests.get(f'http://192.168.1.109:80/chain')
    except requests.exceptions.ConnectionError as e:
        print(f'{e}')
        return False
    length = response.json()['length']
    chain = json.loads(response.json()['chain'].replace("'", '"'))
    return chain


def play():
    global current_block

    while True:
        chain = get_current_chain()
        len_chain = len(chain)

        while len_chain > current_block:
            # press key: press_key(keys['left'], 10)
            character = create_block(chain[current_block]).hash[-1]
            result = ord(character) % len(k)

            press_key(keys[k[result]], 1)
            current_block += 1


if __name__ == '__main__':
    play()

"""
TODO

use requests to get the chain from a known node
calculate the character mapping split based on ending hash
apply kb input each time there is a new block
Create mining methods to mine specific inputs
stream pokemon
"""