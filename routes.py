import json

import requests
from flask import Blueprint, jsonify, request
from node import PokeNode

api_blueprint = Blueprint('api_blueprint', __name__)
consensus_blueprint = Blueprint('consensus_blueprint', __name__) # unused


pn = PokeNode()


@api_blueprint.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': str(pn.blockchain.chain),
        'length': len(pn.blockchain.chain),
    }
    return jsonify(response), 200


@api_blueprint.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        pn.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(pn.nodes),
    }
    return jsonify(response), 201


@api_blueprint.route('/chain/add', methods=['POST'])
def add_block():
    values = request.json
    block = values.get('block')

    result = pn.add_block(block)
    response = {
        'message': f'valid_block={result}',
        'new_block': block,
    }
    return jsonify(response), 201


@api_blueprint.route('/nodes/all', methods=['GET'])
def get_nodes():
    response = {'nodes': [n for n in pn.nodes]}
    return jsonify(response), 201


@api_blueprint.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = pn.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': str(pn.blockchain.chain)
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': str(pn.blockchain.chain)
        }

    return jsonify(response), 200