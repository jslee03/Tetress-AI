from referee.game import PlayerColor, Coord
from referee.game.constants import BOARD_N
from referee.game.pieces import PieceType, create_piece
from referee.game.coord import Direction, Vector2


def coords_list(board, color):
    """
    Searches through the board to locate all 'color' tokens and stores them in a 
    list.

    Returns:
        list[Coord] : A list of cooridnates of the color tokens on the board.
    """
    
    coords = []
    
    for coord, playerColor in board.items():
        
        if playerColor == color:
            coords.append(coord)
    
    return coords


def is_valid(board, n):
    """
    Checks if the coordinate 'n' is empty.

    Returns:
        bool: True if empty, False otherwise.
    """
    
    if n in board:
        return False
    else:
        return True


def get_opponent(color):
    """
    Gets the opponent's playing color.

    Returns:
        PlayerColor: RED if red, BLUE otherwise.
    """

    if color == PlayerColor.RED:
        return PlayerColor.BLUE
    else:
        return PlayerColor.RED


def can_place_piece(board, coord, piece):
    """
    Get all possible piece positions for a single piece at a specified coordinate.

    Returns:
        list[Piece]: A list of all possible piece placements.
    """

    possible_pieces = []
    initial_piece = create_piece(piece, coord)

    # Iterate through each coordinate of initial piece
    for piece_coord in initial_piece.coords:
        
        valid_piece = 1
        
        row_diff = coord.r - piece_coord.r # Calculate row difference
        col_diff = coord.c - piece_coord.c # Calculate col difference

        # Update the new coordinate
        movement = Vector2(row_diff, col_diff)
        new_coord = coord + movement

        # Create a piece with the new coordinate
        possible_piece = create_piece(piece, new_coord)

        # Check if possible piece is valid
        for c in possible_piece.coords:
            if c in board:
                valid_piece = 0
                break
        
        if valid_piece:
            possible_pieces.append(possible_piece)
    
    return possible_pieces


def get_possible_actions(board, coords):
    """
    Gets all the possible actions for a player.

    Returns:
        list[Piece]: A list of all possible actions.
    """

    possible_actions = []
    explored_coords = []

    # Find all possible actions by iterating through each adjacent coordinate on board
    for coord in coords:
        
        for direction in Direction:
            
            curr_coord = coord + direction
            
            if is_valid(board, curr_coord) and curr_coord not in explored_coords:
                explored_coords.append(curr_coord)

                for piece_type in PieceType:
                    # Get all possible piece positions for the current piece_type at the curr_coord
                    possible_actions += can_place_piece(board, curr_coord, piece_type)

    # Remove duplicate actions
    unique_pieces = []
    seen_coords = set()

    for piece in possible_actions:
        
        sorted_coords = tuple(sorted(piece.coords))
        
        if sorted_coords not in seen_coords:
            seen_coords.add(sorted_coords)
            unique_pieces.append(piece)
    
    return unique_pieces
 

def remove_line(state, action):
    """
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


def is_terminal(board):
    """
    Checks if the current board state is a terminal state.

    Returns:
        bool: True if terminal state, False otherwise.
    """

    coords_red = coords_list(board, PlayerColor.RED)
    coords_blue = coords_list(board, PlayerColor.BLUE)

    if len(get_possible_actions(board, coords_red)) == 0 or len(get_possible_actions(board, coords_blue)) == 0:
        return True
    else:
        return False