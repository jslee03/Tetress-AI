from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
from .board import get_opponent, get_possible_actions, get_token_num, get_value, apply_action, is_terminal, heuristic_eval
import copy, random
import math

def calc_ucb(parent, child):
    if child.visits == 0:
        return float('-inf')
    
    exploitation_term = child.value / child.visits
    explorlation_term = math.sqrt(math.log(parent.visits) / child.visits)
    ucb = 2 * exploitation_term + explorlation_term

    return ucb

def random_move(node):
    possible_actions = get_possible_actions(node)
    action = random.choice(possible_actions)

    return action

class Node:
    def __init__(self, state, next_color, parent=None, parent_action=None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.next_color = next_color
        self.visits = 0
        self.value = 0
        self.children = []
        self.turn_num = 1 
        # if parent is None else parent.turn_num + 1
    
    def is_fully_expanded(self):
        return len(self.children) == len(get_possible_actions(self))

    def get_untried_action(self):
        possible_actions = get_possible_actions(self)
        temp_node = copy.deepcopy(self)
        
        if len(self.children) == 0:
            return random.choice(possible_actions)

        for action in possible_actions:
            apply_action(temp_node, action, self.next_color)
            for child in self.children:
                # Check if the state of the applied action already exists as a child node
                if temp_node.state != child.state:
                    return action

            
def mcts(root):
    print("ROOT:")
    print(len(root.state))

    for _ in range(5):
        node = root
        # print("ROOT:")
        # print(root.state)

        selected_node = select(node)
        # print("selected\n")


        leaf = expand(selected_node)
        # print("expanded\n")
        # print(leaf.state)
        # print("\n")

        result = simulate(leaf)
        # print("simulated\n")
        # print(result)

        backpropagate(leaf, result)
        # print("backpropagated\n")

        if leaf == selected_node:
            break

    # choose child with highest number of visits
    
    # print(len(root.children))
    max_visit = 0
    max_child = random.choice(root.children)
    for child_node in root.children:
        if child_node.visits > max_visit:
            max_visit = child_node.visits
            max_child = child_node
    
    action = max_child.parent_action

    return action




def select(node):
    # selected_child = copy.deepcopy(node)
    selected_child = node
    
    while selected_child.is_fully_expanded():
        if (is_terminal(selected_child)[0]):
            break
        # print("bnm")
        # Select a child using UCB1 algorithm
        max_ucb = float('-inf')
        
        for child in selected_child.children:
            ucb = calc_ucb(node, child)
            # print("ucb is: ", ucb)
            if ucb >= max_ucb:
                max_ucb = ucb
                selected_child = child

    return selected_child

def expand(node):
    if node.is_fully_expanded():
        return node

    action = node.get_untried_action()
    child_board = copy.deepcopy(node.state)
    child_node = Node(child_board, get_opponent(node.next_color), node, action)
    apply_action(child_node, action, node.next_color)
    node.children.append(child_node)
    # print(child_node.state)
    # print(action)

    return child_node


def simulate(node: Node):
    temp_node = copy.deepcopy(node)
    possible_actions = None

    # simulate
    for i in range(3):

        game_end = is_terminal(temp_node)[0]

        if game_end:
            break

        possible_actions = get_possible_actions(temp_node)
        rand_action = random.choice(possible_actions)
        apply_action(temp_node, rand_action, temp_node.next_color)
        temp_node.next_color = get_opponent(temp_node.next_color)
        temp_node.turn_num += 1

    
    return heuristic_eval(temp_node.state, temp_node.next_color, temp_node.parent_action)
    # heuristic_eval(temp_node.state, temp_node.next_color, temp_node.parent_action, len(possible_actions))

    """
    red_count, blue_count = get_token_num(temp_node.state)
    # print("red: ", red_count, " blue: ", blue_count)

    if red_count > blue_count:
        return PlayerColor.RED, get_value(temp_node.state, PlayerColor.RED)
    elif blue_count > red_count:
        return PlayerColor.BLUE, get_value(temp_node.state, PlayerColor.BLUE)
    else:
        return None, 0
    """
        
def backpropagate(node, value):
    curr_node = node

    while curr_node is not None:
        curr_node.visits += 1

        if node.next_color == curr_node.next_color:
            curr_node.value += value
        else:
            curr_node.value -= value

        curr_node = curr_node.parent


