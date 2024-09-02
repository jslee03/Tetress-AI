from referee.game import PlayerColor, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, create_piece
from referee.game.coord import Direction, Vector2


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
            # print(possible_piece)
    
    return possible_pieces


def get_possible_actions(board, coords):
    possible_actions = []
    explored_coords = []
    # print(coords)
    for coord in coords:
        for direction in Direction:
            curr_coord = coord + direction
            
            if is_valid(board, curr_coord) and curr_coord not in explored_coords:
                explored_coords.append(curr_coord)
                # print(curr_coord)
                for piece_type in PieceType:
                    # print("PIECE TYPE: ", piece_type)
                    # get all possible piece positions that can be placed for the current piece_type

                    # print(len(can_place_piece(board, curr_coord, piece_type)))
                    possible_actions += can_place_piece(board, curr_coord, piece_type)

    # remove duplicates
    unique_pieces = []
    seen_coords = set()

    for piece in possible_actions:
        sorted_coords = tuple(sorted(piece.coords))
        
        if sorted_coords not in seen_coords:
            seen_coords.add(sorted_coords)
            unique_pieces.append(piece)
    
    # print("TOTAL: ", len(unique_pieces))
    return unique_pieces


    
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
                