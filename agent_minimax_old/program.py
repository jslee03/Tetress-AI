# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from .board import coords_list, get_opponent, get_possible_actions, remove_line, is_valid, can_place_piece
from .minimax import best_move, random_move
import random





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
        self.turn_count = 1


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        board = self.board 
        color = self._color
        turn_count = self.turn_count
        RANDOM_THRESHOLD = 20

        # Scan and find sources
        coords = coords_list(board, color)
        possible_actions = []
        rand_action = random.choice(list(PieceType))

        # Places the player's first piece at random
        if not coords:
            while len(possible_actions) == 0:
                # Generate a random row and column for a random Coord
                random_row = random.randint(0, BOARD_N - 1)
                random_col = random.randint(0, BOARD_N - 1)
                random_coord = Coord(random_row, random_col)

                possible_actions = can_place_piece(board, random_coord, rand_action)
            action = possible_actions[0]
    
        elif turn_count <= RANDOM_THRESHOLD: 
            action = random_move(board, coords, get_possible_actions(board, coords))
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
        remove_line(self.board, action)

        self.turn_count += 1
        # print("UPDATED BOARD: \n")
        # print(self.board)

        red_token = list(self.board.values()).count(PlayerColor.RED)
        blue_token = list(self.board.values()).count(PlayerColor.BLUE)

        print(f"red: {red_token} || blue: {blue_token}")
        

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
   


