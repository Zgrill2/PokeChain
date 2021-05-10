"""
    Difficulty Algorithm:
        difficulty = genesis_difficulty
        If tb.index % 50 == 0:
            From tb.index-50 -> tb.index, if average time between blocks > desired, +1 diff, if < desired -1 diff

    Required Use Cases
        Calculate what the current difficulty should be from a chain
        Calculate what the difficulty of any given block in a chain should be
"""

TARGET_TIME_PER_BLOCK = .51


# Main Diff Algorithm Implementation Here
def calc_chain_head_difficulty(chain):
    difficulty = 0
    for b in chain:
        if b.index == 0:
            difficulty = b.difficulty # set difficulty to 0 at start of chain
        elif b.index % 50 == 0:
            timestamps = []
            past_50 = chain[b.index-50:b.index+1] # get [0-50], [50-100] (inclusive)
            for index in range(len(past_50)-1):
                timestamps.append(past_50[index+1] - past_50[index])
            average_diff = sum(timestamps) / len(timestamps)
            if average_diff > TARGET_TIME_PER_BLOCK:
                difficulty -= 1
            elif average_diff < TARGET_TIME_PER_BLOCK:
                difficulty += 1
    return difficulty


def calc_difficulty_of_block(target_index, chain):
    return calc_chain_head_difficulty(chain[:target_index])


def is_valid_difficulty(block, chain):
    # validates the difficulty in a proposed new block
    return block.difficulty == calc_difficulty_of_block(block.index, chain)


def validate_chain(chain):
    """
    Determine if a given blockchain is valid
    :param chain: A list of Block objects
    :return: <bool> True if valid, False if not
    """
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
        block = chain[current_index]

        verify_block(block, last_block)

        last_block = block
        current_index += 1

    return True


def verify_block(block, previous_block):
    # check the block index iterates properly
    if not previous_block.index+1 == block.index:
        return False

    # Check that the last hash of the block is correct
    if block.previous_hash != previous_block.hash:
        return False

    # Check that the Proof of Work is correct
    if not block.is_valid_proof(block.hash):
        return False
    return True
