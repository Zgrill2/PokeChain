import json
import time
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

current_block = 122000
blockchain = []

from block import Block


def create_block(bdict):
    return Block(bdict["index"], bdict["timestamp"], bdict["previous_hash"], bdict["difficulty"], bdict["nonce"])


def get_current_chain():
    global current_block
    try:
        response = requests.get(f'http://192.168.1.117:5000/chain/{current_block}', timeout=5)
    except requests.exceptions.ConnectionError as e:
        print(f'{e}')
        return False
    length = response.json()['length']
    if length > 0:
        chain = json.loads(response.json()['chain'].replace("'", '"'))
        return chain
    else:
        return False


def play():
    global current_block

    while True:
        chain = get_current_chain()
        #current_block = 0
        if isinstance(chain, bool):
            continue
        len_chain = len(chain)
        head = len_chain + current_block
        i = 0
        while head > i and i < len(chain):
            # press key: press_key(keys['left'], 10)
            character = create_block(chain[i]).hash[-1]
            result = ord(character) % len(k)

            print(f'{k[result]} pressed')
            press_key(keys[k[result]], 1)
            i += 1
            time.sleep(0.25)
        current_block = head


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