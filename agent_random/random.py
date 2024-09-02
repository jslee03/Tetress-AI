from .board import get_possible_actions, coords_list
import random

def random_move(board, coords):
    possible_actions = get_possible_actions(board, coords)
    action = random.choice(possible_actions)

    return action
