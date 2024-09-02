# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.pieces import PieceType, _TEMPLATES, create_piece
from referee.game.coord import Direction, Vector2
from .mcts import *
from .board import *
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
        self.board = {}
        self.root = Node(self.board, color)
        self.turn_count = 1


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
        turn_count = self.turn_count
        RANDOM_THRESHOLD = 20

        if turn_count <= RANDOM_THRESHOLD: 
            action = random_move(self.root)
        else:
            action = mcts(self.root)


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

        remove_line_2(self.board, action)

        self.turn_count += 1
        
        # print("UPDATE FUNTION")
        # print(self.board)
        prev_turn_num = self.root.turn_num

        # Update the root
        if color == self.root.next_color:
            self.root = Node(self.board, color)
            self.root.turn_num = prev_turn_num + 1
        else:
            self.root = Node(self.board,get_opponent(color))
            self.root.turn_num = prev_turn_num + 1


        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")

