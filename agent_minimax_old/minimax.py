from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
from .board import coords_list, get_opponent, get_possible_actions, remove_line, is_terminal, apply_action
import copy, random
import math


TERMINATE_VAL = 0
count = 0
tlrks = 0
test = 0


"asdfasdfasdfasdf"
def random_move(board, coords, possible_actions):
    action = random.choice(possible_actions)

    return action

def best_move(board:dict, coords, color):

    global count
    global tlrks

    
    alpha = -math.inf
    beta = math.inf
    best_move = None
    best_eval = -math.inf

    

    possible_actions = get_possible_actions(board, coords)
    
    depth = get_terminate_val(len(possible_actions))

    print(len(possible_actions))
    
    # if len(possible_actions) >= 100:
    #     print("holllllaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #     return random_move(board, coords, possible_actions)

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
        eval = minimax(temp_board, depth, color, alpha, beta, False, action, len(possible_actions))

        # store if best action
        if eval >= best_eval:
            best_eval = eval
            best_move = action

    print("best_eval", best_eval)
    return best_move                


def minimax(board, depth, color, alpha, beta, max_player, piece, num_actions):
    # print(depth)
    global count


    # NEED TO CONSIDER GAMEOVER
    if depth == 0 or is_terminal(board):
        count += 1
        return heuristic_eval(board, color, piece, num_actions, max_player)
    
    
    if max_player:
        
        max_eval = -math.inf
        coords = coords_list(board, color)
        
        possible_actions = get_possible_actions(board, coords)

        #print("MAX POSSIBLE ACTIONS: ", len(possible_actions))

        for action in possible_actions:

            c1, c2, c3, c4 = action.coords

    
            # Update the board/apply action
            temp_state = copy.deepcopy(board)
            temp_state[c1] = color
            temp_state[c2] = color
            temp_state[c3] = color
            temp_state[c4] = color
            remove_line(temp_state, action)
            
            # minimax (test action)
            eval = minimax(temp_state, depth - 1, color, alpha, beta, False, action, len(possible_actions))
            
            max_eval = max(max_eval, eval)

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
                            
        return max_eval
            
    else:
        
        min_eval = math.inf
        coords = coords_list(board, get_opponent(color))
        possible_actions = get_possible_actions(board, coords)

        #print("MIN POSSIBLE ACTIONS: ", len(possible_actions))

        for action in possible_actions:
        
            c1, c2, c3, c4 = action.coords
            
            # Update the board/apply action
            temp_state = copy.deepcopy(board)
            temp_state[c1] = get_opponent(color)
            temp_state[c2] = get_opponent(color)
            temp_state[c3] = get_opponent(color)
            temp_state[c4] = get_opponent(color)
            remove_line(temp_state, action)
            
            # minimax (test action)
            eval = minimax(temp_state, depth - 1, color, alpha, beta, True, action, len(possible_actions))
            
            min_eval = min(min_eval, eval)
            # if min_eval > eval:
            #     min_eval = eval

            beta = min(beta, eval)
            if beta <= alpha:
                break
                            
        return min_eval

def get_terminate_val(num_actions):
    if num_actions <= 5:
        depth = 2
    elif 5 < num_actions <= 200:
        depth = 1
    else:
        depth = 0
    
    return depth

def heuristic_eval(board, color, piece, num_actions, max_player):
    count_val = count_check(board, color)
    hole_val = hole_check(board, color)
    is_risky = risky_line_check(board, color, piece)
    block_val = block_opponent_check
    # can_win = win_check(board, color, max_player)

    # if can_win == color:
    #     eval = math.inf
    #     return eval
    # elif can_win == get_opponent(color):
    #     eval = -math.inf
    #     return eval
    if block_val == 0:
        eval = math.inf
        return eval

    if is_risky:
        risk_val = -1
    else:
        risk_val = 1

    #eval = 3 * count_val + 2 * hole_val + 3 * risk_val
    adder = 0
    #if num_actions > 20:
    if num_actions: 
        adder = -30 * (1 / num_actions) 
    eval = count_val + (3 * risk_val) + adder + block_val
    
    
    return eval

# Checks winning condition - returns true if opponent cannot place a piece
def win_check(board, color, max_player):
    if max_player:
        last_turn_color = color
    else:
        last_turn_color = get_opponent(color)

    coords_red = coords_list(board, PlayerColor.RED)
    coords_blue = coords_list(board, PlayerColor.BLUE)

    # Terminal if I'm red and blue cannot place action
    if last_turn_color == PlayerColor.RED:
        if len(get_possible_actions(board, coords_blue)) == 0:
            return PlayerColor.RED

        
    # Terminal if I'm blue and red cannot place action
    if last_turn_color == PlayerColor.BLUE:
        if len(get_possible_actions(board, coords_red)) == 0:
            return PlayerColor.BLUE
        
    return None

def block_opponent_check(board, color):
    return len(get_possible_actions(get_opponent(color)))


    
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