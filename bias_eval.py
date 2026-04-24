from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_chess import FowBoard

import chess
from chess import Bitboard
from utils import score_round

class BiasScorer:
    def __init__(self, biases: dict[str, float]):
        self.biases = biases  # The bias dictionary passed from the engine
        self.piece_value_dict = { # Values assigned to each piece type for vision scoring (can be changed from here as needed)
            "king" : 10,
            "queen" : 8,
            "rook" : 5,
            "bishop" : 3, 
            "knight" : 3,
            "pawn" : 1
            }

    def move_bias_applicator(self, move: chess.Move, stockfish_score: int, board: FowBoard, vision_before_score: float) -> int:
        """Adjusts the stockfish score of a move based on certain biasing parameters."""
        # TODO MAKE this a developer setting???
        #if not self.biases:
        #    return stockfish_score  # No bias provided, return the Stockfish score as-is

        # Move Bias Applicator code
        
        counter_move_score = self.get_counter_move_score(move, board) * 50 # Adds 50 score when the move targets the bias piece
        
        vison_weight = 5
        vision_score =  vison_weight * self.get_vision_score(move, board, vision_before_score) # TODO is this still true? #Tends to return a negative score especially when the suggested move captures a piece
        
        target_piece_type = board.piece_type_at(move.to_square)
        if target_piece_type:
            target_piece_name = chess.PIECE_NAMES[target_piece_type]
            capture_bias_coefficient = 0.5
            vision_score += self.piece_value_dict[target_piece_name]  * (1 + capture_bias_coefficient * self.biases.get(target_piece_name, 0)) # Adds reward when move targets a piece to balance lost score for vision after
        
        #risk_score = self.get_risk_score(move, board) * 10 # Subtracts 10 score for each angle of attack exposed to with the passed move
        risk_score = 0 
        return score_round(stockfish_score + counter_move_score + vision_score - risk_score)
    
    def get_counter_move_score(self, move: chess.Move, board: FowBoard) -> float:
        """Returns the bias coefficient against the piece at the target square."""
        target_piece_type = board.piece_type_at(move.to_square)
        if target_piece_type:
            target_piece_name = chess.PIECE_NAMES[target_piece_type]
            return self.biases.get(target_piece_name, 0)  #if target is a biased piece get the bias coefficient
        return 0

    def get_before_vision_score(self, board: FowBoard) -> float: 
        """Analyze vision state of board before move."""

        # Initialize variables for calculation
        piece_values = 0
        visibility: Bitboard = board.get_fow_visibility()
        tile_value = visibility.bit_count()
        visible_opponent: Bitboard = visibility & board.occupied_co[not board.turn]

        # Sum piece values of visible opponent pieces
        vision_bias_coefficient = 0.5
        piece_values += self.piece_value_dict["pawn"] * (visible_opponent & board.pawns).bit_count() * (1 + vision_bias_coefficient * self.biases.get("pawn", 0))
        piece_values += self.piece_value_dict["knight"] * (visible_opponent & board.knights).bit_count() * (1 + vision_bias_coefficient * self.biases.get("knight", 0))
        piece_values += self.piece_value_dict["bishop"] * (visible_opponent & board.bishops).bit_count() * (1 + vision_bias_coefficient * self.biases.get("bishop", 0))
        piece_values += self.piece_value_dict["rook"] * (visible_opponent & board.rooks).bit_count() * (1 + vision_bias_coefficient * self.biases.get("rook", 0))
        piece_values += self.piece_value_dict["queen"] * (visible_opponent & board.queens).bit_count() * (1 + vision_bias_coefficient * self.biases.get("queen", 0))
        piece_values += self.piece_value_dict["king"] * (visible_opponent & board.kings).bit_count() * (1 + vision_bias_coefficient * self.biases.get("king", 0))

        vision_before = tile_value + piece_values

        return vision_before

    def get_vision_score(self, move_to_make: chess.Move, board: FowBoard, vision_before: float) -> float:
        """Analyze vision state of board after move and return a score accordingly."""
        # Simulate move
        board.push(move_to_make) # Push move to make so that it can be analyzed
        board.push(chess.Move.null()) # Push null move to make it white's turn

        # Initialize variables for calculation
        piece_values = 0
        visibility: Bitboard = board.get_fow_visibility() 
        tile_value = visibility.bit_count()
        visible_opponent: Bitboard = visibility & board.occupied_co[not board.turn]

        # Sum piece values of visible opponent pieces
        vision_bias_coefficient = 0.5
        piece_values += self.piece_value_dict["pawn"] * (visible_opponent & board.pawns).bit_count() * (1 + vision_bias_coefficient * self.biases.get("pawn", 0))
        piece_values += self.piece_value_dict["knight"] * (visible_opponent & board.knights).bit_count() * (1 + vision_bias_coefficient * self.biases.get("knight", 0))
        piece_values += self.piece_value_dict["bishop"] * (visible_opponent & board.bishops).bit_count() * (1 + vision_bias_coefficient * self.biases.get("bishop", 0))
        piece_values += self.piece_value_dict["rook"] * (visible_opponent & board.rooks).bit_count() * (1 + vision_bias_coefficient * self.biases.get("rook", 0))
        piece_values += self.piece_value_dict["queen"] * (visible_opponent & board.queens).bit_count() * (1 + vision_bias_coefficient * self.biases.get("queen", 0))
        piece_values += self.piece_value_dict["king"] * (visible_opponent & board.kings).bit_count() * (1 + vision_bias_coefficient * self.biases.get("king", 0))

        # Undo simulated move
        board.pop() # Undo null move
        board.pop() # Undo move to make

        vision_after = tile_value + piece_values

        return vision_after - vision_before

    # Depreciated method? TODO Figure out the deal with risk score
    #def get_risk_score(self, move_to_make, board):
    #    """Counts the number of black pieces that can attack the destination square"""
    #    angles_of_attack = board.attackers(False, move_to_make.to_square)
    #    return len(angles_of_attack)