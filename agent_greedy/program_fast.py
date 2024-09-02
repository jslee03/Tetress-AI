# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
import copy, random
import math

TERMINATE_VAL = 2


# class Node:
#     def __init__(self, action, color, eval=0):
#         self.action = action
#         self.color = color
#         self.eval = eval
#         self.children = []
    
#     def is_fully_expanded(self):
#         return len(self.children) == len(get_possible_actions(self))
    
#     def get_untried_action(self):
#         possible_actions = get_possible_actions(self)
#         temp_node = copy.deepcopy(self)
        
#         if len(self.children) == 0:
#             return random.choice(possible_actions)
        
#         for action in possible_actions:
#             apply_action(temp_node, action, self.color)
#             for child in self.children:
#                 # Check if the state of the applied action already exists as a child node
#                 if temp_node.state != child.state:
#                     return action
        


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        self.board = {} ### PROBLEM ###
        #self.root = Node(self.board, color)

        # match color:
        #     case PlayerColor.RED:
        #         print("Testing: I am playing as RED")
        #     case PlayerColor.BLUE:
        #         print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        board = self.board 
        color = self._color
        
        # Scan and find sources
        coords = coords_list(board, color)

        # Places the player's first piece at random
        if not coords:
            pieces = []
            for piece in PieceType:
                pieces.append(piece)
            
            # Tries actions until one is valid
            while True:
                rand_piece = random.choice(pieces)
                r = random.randint(0,10)
                c = random.randint(0,10)
                action = create_piece(rand_piece, Coord(r,c))
                if valid_action(board, action):
                    break
        
        else: 
            action = best_move(board, coords, color)
    
        return PlaceAction(
            action.coords[0], 
            action.coords[1], 
            action.coords[2], 
            action.coords[3]
        )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords
        
        # Update the board
        self.board[c1] = color
        self.board[c2] = color
        self.board[c3] = color
        self.board[c4] = color

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
   


def best_move(board, coords, color):
    
    alpha = -math.inf
    beta = math.inf
    best_move = None
    eval = -math.inf
    best_eval = -math.inf
    action_store = []
    
    
    possible_actions = get_possible_actions(board, coords)

    for action in possible_actions:
        c1, c2, c3, c4 = action.coords
        
        # Update the board/apply action
        temp_board = copy.deepcopy(board)
        temp_board[c1] = color
        temp_board[c2] = color
        temp_board[c3] = color
        temp_board[c4] = color
        remove_line(temp_board, action)
        
        #print(improvement_in_heur(temp_board, color), color, board.items())
        if improvement_in_heur(temp_board, color):
            print("\nhollllllllllllaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n")
            eval = minimax(temp_board, 0, get_opponent(color), alpha, beta, False)
        else:
            action_store.append(action)
            
        # store if best action
        if eval > best_eval:
            best_eval = eval
            best_move = action
        
        elif eval == -math.inf:
            best_move = random.choice(action_store)
    
    # # Obtain the best move for each source block
    # for block in coords:
        
    #     for move in Direction:
            
    #         origin = block + move
            
    #         if is_valid(board, origin):
                
    #             for tetromino in PieceType:
                    
    #                 #action
    #                 action = create_piece(tetromino, origin)
    #                 c1, c2, c3, c4 = action.coords
                    
    #                 if valid_action(board, action):
                    
    #                     # Update the board/apply action
    #                     temp_board = copy.deepcopy(board)
    #                     temp_board[c1] = color
    #                     temp_board[c2] = color
    #                     temp_board[c3] = color
    #                     temp_board[c4] = color
                        
    #                     # minimax (test action)
    #                     #if color == PlayerColor.BLUE: print("First", best_eval, color)
    #                     eval = minimax(temp_board, 0, get_opponent(color), alpha, beta, False)
    #                     #if color == PlayerColor.BLUE: print("Second",eval, best_eval, color)
    #                     # store if best action
    #                     if eval > best_eval:
    #                         best_eval = eval
    #                         best_move = action

    
    return best_move                


def minimax(board, depth, color, alpha, beta, max_player):

    # NEED TO CONSIDER GAMEOVER
    if depth == TERMINATE_VAL:
        return heuristic_eval(board, color)
    
    if max_player:
        
        max_eval = -math.inf
        coords = coords_list(board, color)
        possible_actions = get_possible_actions(board, coords)

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
            eval = minimax(temp_state, depth + 1, color, alpha, beta, False)
            
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
                            
        return max_eval
            
    else:
        
        min_eval = math.inf
        coords = coords_list(board, color)
        possible_actions = get_possible_actions(board, coords)

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
            eval = minimax(temp_state, depth + 1, get_opponent(color), alpha, beta, True)
            
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
                            
        return min_eval


# Obtains a list of all the source blocks of the current color
def coords_list(board, color):
    coords = []
    for coord, playerColor in board.items():
        if playerColor == color:
            coords.append(coord)
    return coords	


# Checks if the node is valid
def is_valid(board, n):
	if n in board:
		return False
	else:
		return True


def heuristic_eval(board, color):
    player = 0
    opponent = 0
    for playerColor in board.values():
        if playerColor == color:
            player += 1
        else:
            opponent += 1
    return player - opponent


def improvement_in_heur(board, color):
    if color == PlayerColor.RED:
        if heuristic_eval(board, color) > 4:
            return 1
    else:
        if heuristic_eval(board, color) > 0:
            return 1
    return 0


def valid_action(board, action):
    for i in range(len(action.coords)):
        if action.coords[i] in board:
            return False
    return True   


def get_opponent(color):
    if color == PlayerColor.RED:
        return PlayerColor.BLUE
    else:
        return PlayerColor.RED


###############################################################################################################################################\
def can_place_piece(board, coord, piece):
    possible_pieces = []
    initial_piece = create_piece(piece, coord)

    for piece_coord in initial_piece.coords:
        valid_piece = 1
        row_diff = coord.r - piece_coord.r
        col_diff = coord.c - piece_coord.c

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


def get_possible_actions(board, coords):
    possible_actions = []
    for coord in coords:
        for direction in Direction:
            curr_coord = coord + direction
            if is_valid(board, curr_coord):
                for piece_type in PieceType:
                    # get all possible piece positions that can be placed for the current piece_type
                    possible_actions += can_place_piece(board, curr_coord, piece_type)

    # remove duplicates
    possible_actions = list(set(possible_actions))
    return possible_actions

def get_possible_actions_2(node):
    # Find all coordinates for my current tokens
    my_tokens = []
    possible_actions = []
    for token, color in node.state.items():
        if color == node.playing_color:
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
    
    
def apply_action(node, piece, color):
    node.parent_action = piece
    for coord in piece.coords:
        node.state[coord] = color
    remove_line(node.state, piece)
        

def remove_line(state, action):
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
            del state[Coord(r, c)]

    # Removes all the complete columns
    for c in complete_cols:
        for r in range(BOARD_N):
            if r not in complete_rows:
                del state[Coord(r, c)]
                

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