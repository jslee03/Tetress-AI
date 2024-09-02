from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
from .mcts import *
import copy, random
import math

def get_opponent(next_color):
    if next_color == PlayerColor.RED:
        return PlayerColor.BLUE
    else:
        return PlayerColor.RED


def can_place_piece(board, coord, piece):
    possible_pieces = []
    initial_piece = create_piece(piece, coord)

    for piece_coord in initial_piece.coords:
        valid_piece = 1
        row_diff = coord.r - piece_coord.r
        # row = Coord(abs(row_diff, 0))
        col_diff = coord.c - piece_coord.c
        # col = Coord(0, abs(col_diff))

        movement = Vector2(row_diff, col_diff)
        new_coord = coord + movement
        possible_piece = create_piece(piece, new_coord)

        # check if possible piece is valid
        for c in possible_piece.coords:
            if c in board:
                valid_piece = 0
                break
        
        if valid_piece:
            possible_pieces.append(possible_piece)
    
    return possible_pieces


def get_possible_actions(node):
    # Find all coordinates for my current tokens
    my_tokens = []
    possible_actions = []
    for token, color in node.state.items():
        if color == node.next_color:
            my_tokens.append(token)
        
    """
    # If no tokens for my color exists, action can be placed anywhere
    if len(my_tokens) == 0:
        for row in range(BOARD_N):
            for col in range(BOARD_N):
                if Coord(row, col):
                    my_tokens.append(Coord(row, col))
    """
    # If no tokens for my color exist
    if len(my_tokens) == 0:
        rand_action = random.choice(list(PieceType))
        possible_actions = []

        while len(possible_actions) == 0:
            # Generate a random row and column for a random Coord
            random_row = random.randint(0, BOARD_N - 1)
            random_col = random.randint(0, BOARD_N - 1)
            random_coord = Coord(random_row, random_col)

            possible_actions = can_place_piece(node.state, random_coord, rand_action)

        return possible_actions
    
    for coord in my_tokens:
        for direction in Direction:
            curr_coord = coord + direction
            if curr_coord not in node.state and curr_coord not in my_tokens:
                for piece_type in PieceType:
                    # get all possible piece positions that can be placed for the current piece_type
                    possible_actions += can_place_piece(node.state, curr_coord, piece_type)

    # remove duplicates
    possible_actions = list(set(possible_actions))
    return possible_actions

def apply_action(node, piece, color):
    node.parent_action = piece
    for coord in piece.coords:
        node.state[coord] = color
    remove_line(node, piece)

    return 0

def remove_line(node, action):
    """
    FROM PROJECT PART A
    Checks if any lines of the placed tetromino are completely filled and 
    removes all completed lines from the board.

    Returns:
        None
    """
    rows = set()         # Stores unqiue rows that should be checked
    cols = set()         # Stores unique cols that should be checked
    complete_rows = []   # Stores all complete rows needed to be removed
    complete_cols = []   # Stores all complete cols needed to be removed

    # Appends unique rows and columns
    for coord in action.coords:
        rows.add(coord.r)
        cols.add(coord.c)

    # Checks if any rows are complete
    for r in rows:
        row_complete = True
        # Iterates through all cells in the row
        for c in range(BOARD_N):
            if Coord(r, c) not in node.state:
                row_complete = False
                break
        if row_complete:
            complete_rows.append(r)

    # Checks if any columns are complete
    for c in cols:
        col_complete = True
        # Iterates through all cells in the column
        for r in range(BOARD_N):
            if Coord(r, c) not in node.state:
                col_complete = False
                break
        if col_complete:
            complete_cols.append(c)

    # Removes all the complete rows
    for r in complete_rows:
        if all(Coord(r, c) in node.state for c in range(BOARD_N)):
            for c in range(BOARD_N):
                # print("REMOVE ALL COORDS IN ROW: ", r)
                del node.state[Coord(r, c)]

    # Removes all the complete columns
    for c in complete_cols:
        if all(Coord(r, c) in node.state for r in range(BOARD_N)):
            for r in range(BOARD_N):
                # print("REMOVE ALL COORDS IN COL: ", c)
                del node.state[Coord(r, c)]

def remove_line_2(state, action):
    """
    FROM PROJECT PART A
    Checks if any lines of the placed tetromino are completely filled and 
    removes all completed lines from the board.

    Returns:
        None
    """
    rows = set()         # Stores unqiue rows that should be checked
    cols = set()         # Stores unique cols that should be checked
    complete_rows = []   # Stores all complete rows needed to be removed
    complete_cols = []   # Stores all complete cols needed to be removed

    # Appends unique rows and columns
    for coord in action.coords:
        rows.add(coord.r)
        cols.add(coord.c)

    # Checks if any rows are complete
    for r in rows:
        row_complete = True
        # Iterates through all cells in the row
        for c in range(BOARD_N):
            if Coord(r, c) not in state:
                row_complete = False
                break
        if row_complete:
            complete_rows.append(r)

    # Checks if any columns are complete
    for c in cols:
        col_complete = True
        # Iterates through all cells in the column
        for r in range(BOARD_N):
            if Coord(r, c) not in state:
                col_complete = False
                break
        if col_complete:
            complete_cols.append(c)

    # Removes all the complete rows
    for r in complete_rows:
        for c in range(BOARD_N):
            print("REMOVE ALL COORDS IN ROW: ", r)
            del state[Coord(r, c)]

    # Removes all the complete columns
    for c in complete_cols:
        for r in range(BOARD_N):
            if r not in complete_rows:
                print("REMOVE ALL COORDS IN COL: ", c)
                del state[Coord(r, c)]

def is_terminal(node):

    winner = None

    # Check if max turns reached
    if node.turn_num >= MAX_TURNS:
        red_token, blue_token = get_token_num(node.state)
        if red_token > blue_token:       # red win
            winner = PlayerColor.RED
            return True, winner
        elif red_token < blue_token:     # blue win
            winner = PlayerColor.BLUE
            return True, winner
        else:                            # draw, winner = None
            return True, winner


    # If player cannot place an action, opponent is declared the winner
    curr_node = copy.deepcopy(node)
    # curr_node.next_color = get_opponent(node.next_color)

    if len(get_possible_actions(curr_node)) == 0:
        if curr_node.next_color == PlayerColor.BLUE:
            winner = PlayerColor.RED
        else:
            winner = PlayerColor.BLUE
        return True, winner
    else:
        # game is not finished
        return False, winner
    

def get_token_num(state):
    red_token = list(state.values()).count(PlayerColor.RED)
    blue_token = list(state.values()).count(PlayerColor.BLUE)

    return red_token, blue_token


def get_value(state, color):
    red_token, blue_token = get_token_num(state)

    if color == PlayerColor.RED:
        return red_token - blue_token
    else:
        return blue_token - red_token
    

def heuristic_eval(board, color, piece):
    count_val = count_check(board, color)
    hole_val = hole_check(board, color)
    is_risky = risky_line_check(board, color, piece)

    if is_risky:
        risk_val = -1
    else:
        risk_val = 1

    eval = 3 * count_val + 2 * hole_val + 3 * risk_val

    return eval


# def heuristic_eval(board, color, piece, num_actions):
#     count_val = count_check(board, color)
#     hole_val = hole_check(board, color)
#     is_risky = risky_line_check(board, color, piece)

#     if is_risky:
#         risk_val = -1
#     else:
#         risk_val = 1

#     adder = 0
#     #if num_actions > 20:
#     if num_actions: 
#         adder = -20 * (1 / num_actions) 
#     eval = count_val + (3 * risk_val) + adder 
    
#     return eval

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