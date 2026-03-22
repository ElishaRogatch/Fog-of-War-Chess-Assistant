from tkinter import messagebox
import chess

class GameOver: 
    def __init__(self, root, board):
        self.root = root
        self.board = board
        self.engine = None
        
    def assign_engine(self, engine):
        self.engine = engine
        
    def assign_wait_lock(self, wait_lock):
        self.wait_lock = wait_lock

    def quit_game(self):
        # Close chess engine
        self.engine.close_engine()
        
        # Make sure the player transition is completed
        self.wait_lock.set(2) # Quit
        
        # Close the GUI window
        self.root.destroy()
        print("Game ended")

    def check_game_over(self):
        """Check if the game is over."""
        game_outcome = self.board.outcome()
        if game_outcome is not None: # Check all game over conditions
            if game_outcome.termination == chess.Termination.VARIANT_LOSS:
                winner = "White" if game_outcome.winner else "Black"
                messagebox.showinfo("King Captured", f"{winner} wins!")
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.FIFTY_MOVES:
                messagebox.showinfo("50 Move Rule", "It's a draw!")
                self.quit_game()
                return True
            elif game_outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                messagebox.showinfo("Threefold Repetition", "It's a draw!")
                self.quit_game()
                return True
        return False