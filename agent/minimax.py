from referee.game import PlayerColor, Coord
from referee.game.constants import BOARD_N
from .board import coords_list, get_opponent, get_possible_actions, remove_line, is_terminal
import copy, random
import math

DEPTH_THRESHOLD = 5
BLOCK_OPPONENT_THRESHOLD = 7
APPROACH_TERM_STATE_VAL = 23

def random_move(possible_actions):
    """
    Selects a random action from a list of all possible actions.
    
    Retturns:
        Action: A randomly chosen action.
    """
    
    action = random.choice(possible_actions)

    return action


def best_move(board:dict, coords, color):
    """
    Finds the best move given a board state using the minimax algorithm.
    
    Returns:
        Action: The best move to make on the board.
    """
        
    alpha = -math.inf
    beta = math.inf
    best_move = None
    best_eval = -math.inf

    possible_actions = get_possible_actions(board, coords)
    explore_full = 0

    # Determines whether we should restrict the breadth of search tree
    if len(possible_actions) < 10:
        best_actions = possible_actions
        explore_full = 1
    else:
        best_actions = select_best_actions(board, color, possible_actions)
    
    # Obtains the depth we will use for the minimax algorithm
    depth = get_depth_val(len(best_actions))
    
    for action in best_actions:
        
        c1, c2, c3, c4 = action.coords
        
        # Update the board/apply action
        temp_board = copy.deepcopy(board)
        temp_board[c1] = color
        temp_board[c2] = color
        temp_board[c3] = color
        temp_board[c4] = color
        remove_line(temp_board, action)
        
        # Minimax (test action)
        eval = minimax(temp_board, depth, color, alpha, beta, False, action, len(best_actions), explore_full)

        # Store move and eval if it is the best action
        if eval >= best_eval:
            best_eval = eval
            best_move = action

    return best_move                


def minimax(board, depth, color, alpha, beta, max_player, piece, num_actions, explore_full):
    """
    Executes the minimax algorithm with alpha-beta pruning and selects the most optimal move.
    
    Returns:
        float: The evaulation value of the best move.
    """

    # Base case for the recursive function that evaluates the heuristic
    if depth == 0 or is_terminal(board):
        return heuristic_eval(board, color, piece, num_actions)
    
    # Tries to find the max evaluation
    if max_player:
        
        max_eval = -math.inf
        coords = coords_list(board, color)
        
        possible_actions = get_possible_actions(board, coords)
        
        # Reduces moves to select best if it has not been explored fully
        if explore_full:
            best_actions = possible_actions
        else:
            best_actions = select_best_actions(board, color, possible_actions)


        for action in best_actions:

            c1, c2, c3, c4 = action.coords
    
            # Update the board/apply action
            temp_state = copy.deepcopy(board)
            temp_state[c1] = color
            temp_state[c2] = color
            temp_state[c3] = color
            temp_state[c4] = color
            remove_line(temp_state, action)
            
            # Minimax (test action)
            eval = minimax(temp_state, depth - 1, color, alpha, beta, False, action, len(best_actions), 
                           explore_full)
            
            max_eval = max(max_eval, eval)

            # Alpha-beta pruning
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
                            
        return max_eval
    
    # Tries to find the min evaluation   
    else:
        
        min_eval = math.inf
        coords = coords_list(board, get_opponent(color))

        possible_actions = get_possible_actions(board, coords)
        
        # Reduces moves to select best if it has not been explored fully
        if explore_full:
            best_actions = possible_actions
        else:
            best_actions = select_best_actions(board, color, possible_actions)
            
        for action in best_actions:
        
            c1, c2, c3, c4 = action.coords
            
            # Update the board/apply action
            temp_state = copy.deepcopy(board)
            temp_state[c1] = get_opponent(color)
            temp_state[c2] = get_opponent(color)
            temp_state[c3] = get_opponent(color)
            temp_state[c4] = get_opponent(color)
            remove_line(temp_state, action)
            
            # Minimax (test action)
            eval = minimax(temp_state, depth - 1, color, alpha, beta, True, action, num_actions, explore_full)
            
            min_eval = min(min_eval, eval)

            # Alpha-beta pruning
            beta = min(beta, eval)
            if beta <= alpha:
                break
                            
        return min_eval


def select_best_actions(board, color, possible_actions):
    """
    Selects the best 20 actions among all possible actions based on a heuristic evaluation.
    
    Returns:
        list[Action]: The selected best actions.
    """
    
    possible_actions_dict = {}

    # Evaluates each action
    for action in possible_actions:

        eval = heuristic_eval(board, color, action, len(possible_actions))
        possible_actions_dict[action] = eval
    
    # Sorts the actions by evaluat
    sorted_actions = sorted(possible_actions_dict.items(), key=lambda item : item[1], reverse=True)

    # Obtains the select best acti 
    best_actions = [item[0] for item in sorted_actions[:min(len(sorted_actions), 20)]]
    
    return best_actions


def get_depth_val(num_actions):
    """
    Dynamically determines the depth of the search tree.

    Returns:
        int: Depth.
    """
    if num_actions <= DEPTH_THRESHOLD:
        depth = 2
    else:
        depth = 1
    
    return depth


def heuristic_eval(board, color, piece, num_actions):
    """
    Calculates the heuristic value depending on 4 different features:
    1. The difference in token count between player and opponent.
    2. The risk of potential loss of blocks when a line is cleared.
    3. The player's flexiblity to place an action.
    4. The opponent's flexibility to place an action.

    Returns:
        float: The heuristic value.
    """

    # Evaluate each of the 4 factors
    count_val = count_check(board, color)
    risk_val = risky_line_check(board, color, piece)
    action_val = action_check(num_actions)

    # Use block_val in heuristic when reaching end of game
    if num_actions < BLOCK_OPPONENT_THRESHOLD:
        block_val = block_opponent_check(board, color)
    else:
        block_val = 0

    # Combine the evaluated values using weighted sums for final evaluation
    if num_actions <= APPROACH_TERM_STATE_VAL:
        eval = count_val + risk_val + 2 * action_val - 3 * block_val
    else:
        eval = count_val + 2 * risk_val + action_val - block_val
    
    return eval


def action_check(num_actions):
    """
    Calculates a decreased negative value for an increase in the number of actions.
    
    Returns:
        float: Evaluated action value.
    """

    action_val = 0
    if num_actions: 
        action_val = -30 * (1 / num_actions)
    return action_val


def block_opponent_check(board, color):
    """
    Calculates the number of possible actions for the oppoenet.

    Returns:
        int: The number of possible actions for opponent.
    """
    coords = coords_list(board, get_opponent(color))
    return len(get_possible_actions(board, coords))

    
def count_check(board, color):
    """
    Calculates the difference between number of player tokens and opponent tokens on the board.

    Returns:
        int: The difference in number of tokens.
    """

    red_token = list(board.values()).count(PlayerColor.RED)
    blue_token = list(board.values()).count(PlayerColor.BLUE)

    if color == PlayerColor.RED:
        return red_token - blue_token
    else:
        return blue_token - red_token


def risky_line_check(board, color, piece):
    """
    Checks if placing a piece would create a risky row or column. A line is considered risky if it has more 
    than 5 blocks of its color.

    Returns:
        int: -1 if a risky row/col is found, 1 otherwise.
    """

    rows = set()         # Stores unqiue rows that should be checked
    cols = set()         # Stores unique cols that should be checked
    risk_val = 1         # Positive 1 indicates not risky

    # Appends unique rows and columns
    for coord in piece.coords:
        rows.add(coord.r)
        cols.add(coord.c)

    # Checks if any rows are risky
    for r in rows:
        block_count = 0
        # Iterates through all cells in the row
        for c in range(BOARD_N):
            if Coord(r, c) in board and board[Coord(r, c)] == color:
                block_count += 1
                if block_count > 5:
                    risk_val = -1
                    return risk_val

    # Checks if any cols are risky
    for c in cols:
        block_count = 0
        # Iterates through all cells in the row
        for r in range(BOARD_N):
            if Coord(r, c) in board and board[Coord(r, c)] == color:
                block_count += 1
                if block_count > 5:
                    risk_val = -1
                    return risk_val

    return risk_val