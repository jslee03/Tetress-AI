from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
from .board import coords_list, get_opponent, get_possible_actions, remove_line, is_terminal, apply_action
import copy, random
import math


TERMINATE_VAL = 1
count = 0
tlrks = 0
test = 0

def greedy_move(board:dict, coords, color):

    global count
    global tlrks


    best_move = None
    best_eval = -math.inf

    

    possible_actions = get_possible_actions(board, coords)

    print(len(possible_actions))

    for action in possible_actions:
        c1, c2, c3, c4 = action.coords
        
        # Update the board/apply action
        temp_board = copy.deepcopy(board)
        temp_board[c1] = color
        temp_board[c2] = color
        temp_board[c3] = color
        temp_board[c4] = color
        remove_line(temp_board, action)
        
        # minimax (test action)
        eval = heuristic_eval(board, color, action, len(possible_actions))

        # store if best action
        if eval > best_eval:
            best_eval = eval
            best_move = action

    print(best_eval)
    return best_move                



def heuristic_eval(board, color, piece, num_actions):
    count_val = count_check(board, color)
    # hole_val = hole_check(board, color)
    risk_val = risky_line_check(board, color, piece)

    # Begin to use block_val in heuristic when there is less than 7 possible moves
    if num_actions < 7:
        block_val = block_opponent_check(board, color)
    else:
        block_val = 0


    action_val = 0
    if num_actions: 
        action_val = -30 * (1 / num_actions) 

    # eval = count_val + (3 * risk_val) + action_val
    if num_actions <= 23:
        eval = count_val + risk_val + 2 * action_val - 3 * block_val
    else:
        eval = count_val + (2 * risk_val) + action_val - block_val
    
    return eval

def block_opponent_check(board, color):
    coords = coords_list(board, get_opponent(color))
    return len(get_possible_actions(board, coords))

# Difference between number of player blocks and opponent blocks on the board
def count_check(board, color):
    red_token = list(board.values()).count(PlayerColor.RED)
    blue_token = list(board.values()).count(PlayerColor.BLUE)
    if color == PlayerColor.RED:
        return red_token - blue_token
    else:
        return blue_token - red_token


# Hole in any line may stablise the line, preventing opponent from clearing the row/col
def hole_check(board, color):
    
    holes = 0
    is_hole = 1
  
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            curr_coord = Coord(r, c)
            for direction in Direction:
                coord_check = curr_coord + direction
                if coord_check in board:
                    if board[coord_check] != color:
                        is_hole = 0
                        break
            if is_hole:
                holes += 1
    
    return holes

# If a line has more than 5 blocks of its color, it is considered a 'risky row/col'
def risky_line_check(board, color, piece):
    rows = set()         # Stores unqiue rows that should be checked
    cols = set()         # Stores unique cols that should be checked
    is_risky = False

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
                    is_risky = True
                    return is_risky

    # Checks if any cols are risky
    for c in cols:
        block_count = 0
        # Iterates through all cells in the row
        for r in range(BOARD_N):
            if Coord(r, c) in board and board[Coord(r, c)] == color:
                block_count += 1
                if block_count > 5:
                    is_risky = True
                    return is_risky

    return is_risky