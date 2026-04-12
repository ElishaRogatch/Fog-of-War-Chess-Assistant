from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_chess import FowBoard
    from fow_logger import FowLogger
    from fow_engine import FowEngine

import tkinter as tk
import chess
from gui_io import MessageOutput

class GameOver: 
    def __init__(self, root, board: FowBoard, logger: FowLogger, names: list[str]):
        self.root = root
        self.board = board
        self.logger = logger
        self.names = names
        
    def assign_engine(self, engine: FowEngine):
        self.engine = engine
        
    def assign_wait_lock(self, wait_lock: tk.IntVar):
        self.wait_lock = wait_lock

    def quit_game(self):
        # Close chess engine
        self.engine.close_engine()
        
        # Make sure the player transition is completed
        self.wait_lock.set(2) # Quit
        
        # Close the GUI window
        self.root.destroy()
        self.logger.log("Game ended")
        
    def force_quit_game(self):
        self.logger.log("Game terminated by user.")
        self.quit_game()

    def check_game_over(self):
        """Check if the game is over."""
        game_outcome: chess.Outcome = self.board.outcome() 
        if game_outcome is not None: # Check all game over conditions
            if game_outcome.termination == chess.Termination.VARIANT_LOSS:
                self.game_over_message(f"{self.names[not game_outcome.winner]}'s king captured: {self.names[game_outcome.winner]} wins!")
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.FIFTY_MOVES:
                self.game_over_message("By 50 move rule it's a draw!")
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                self.game_over_message("By threefold repetition it's a draw!")
                self.quit_game()
                return True
        return False
    
    def game_over_message(self, message_to_show):
        """Display the game result."""
        return MessageOutput(
            parent=self.root,
            message=message_to_show,
            title="Game Over",
            icon_path="images/icons/Endgame.ico",
            wrap_length=280,
            label_padding=(50,5)
        )