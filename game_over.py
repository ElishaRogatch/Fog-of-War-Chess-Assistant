from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_chess import FowBoard
    from fow_logger import FowLogger
    from fow_engine import FowEngine

import tkinter as tk
import chess

class GameOver: 
    def __init__(self, root, board: FowBoard, logger: FowLogger):
        self.root = root
        self.board = board
        self.logger = logger
        
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

    def check_game_over(self):
        """Check if the game is over."""
        game_outcome: chess.Outcome = self.board.outcome() 
        if game_outcome is not None: # Check all game over conditions
            if game_outcome.termination == chess.Termination.VARIANT_LOSS:
                winner = "White" if game_outcome.winner else "Black"
                EndGameOutput(self.root, f"(not winner) king captured: {winner} wins!") # TODO Fix this so that it works with names and is actually th opposite
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.FIFTY_MOVES:
                EndGameOutput(self.root, "By 50 move rule it's a draw!")
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                EndGameOutput(self.root, "By threefold repetition it's a draw!")
                self.quit_game()
                return True
        return False
    
class EndGameOutput(tk.Toplevel):
    """Display the game result."""
    def __init__(self, parent, message):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Endgame.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(200, 150)
        self.title("Game Over")
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=message, wraplength=280).pack(padx=50, pady=5)

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM, padx=10, pady=5)
        
        # Pauses code until answered
        self.wait_window(self)


    def ok(self):
        self.close()
       
    def close(self):
        self.destroy()