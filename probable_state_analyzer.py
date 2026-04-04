from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board_state_limiter import BoardStateLimiter
    from fow_engine import FowEngine
    
import chess
from utils import score_round

class ProbableStateAnalyzer:
    def __init__(self, BSL: BoardStateLimiter, engine: FowEngine, biases: dict[str, float]):
        self.BSL = BSL
        self.engine = engine
        self.board_scores: list[tuple[int, float]] = [(0, 46.0)] # initialize board_states
        self.biases = biases
    
    # Analyze each board state in BSL.board_states    
    def analyze_states(self):
        self.board_scores.clear()
        for i in range(len(self.BSL.board_states)):
            board = self.BSL.board_states[i]
            score = self.engine.board_state_analysis(board) #potentially use multiple engines
            # apply bias to possible states based on biased piece
            for bias in self.biases:
                piece_to_counter = bias
                target_pieces = [chess.PIECE_NAMES[piece_type] for piece_type in board.last_piece_moved]
                piece_chance = target_pieces.count(piece_to_counter) / len(target_pieces) #the chance that the target
                score += 50 * piece_chance * self.biases[bias]
            self.board_scores.append((i, score_round(score)))
        self.board_scores.sort(key=lambda x: x[1], reverse=True) # Sort by score descending   
    
    

    