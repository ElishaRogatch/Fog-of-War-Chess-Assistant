import tkinter as tk
import fow_chess
from fow_engine import FowEngine
from input_processor import InputProcessor
from board_draw import DrawBoard
from play_game import PlayGame
from game_over import GameOver
from fow_logger import FowLogger


class ChessGUI:
    def __init__(self, root):
        """Initialize the main GUI application."""
        self.root = root

        # Initializes board
        self.board = fow_chess.FowBoard()
        self.root.title("Two-Player Fog Of War Chess Game")

        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels

        # Create Canvas to draw chessboard
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        self.canvas.pack()

        # Track which player is the assisted one
        self.assisted_player = fow_chess.WHITE

        # Makes instance of FowLogger
        self.logger = FowLogger()

        # Makes instance of DrawBoard
        self.board_draw = DrawBoard(self.root, self.board, self.board_size, self.square_size, self.canvas)

        # Create an instance of InputProcessor and set a variable for bias
        self.processor = InputProcessor(self.root, self.logger)  
        self.biases = self.processor.bias()

        # Initialize GameOver
        self.game_over = GameOver(self.root, self.board, self.logger)

        # Create an instance of FowEngine
        self.engine = FowEngine(self.root, self.board, self.biases, self.game_over, self.logger)
        self.game_over.assign_engine(self.engine)

        # Make instance of PlayGame
        self.play_game = PlayGame(self.root, self.board, self.canvas, self.square_size, self.assisted_player, self.board_draw, self.game_over, self.engine, self.biases, self.logger)

        # Initialize game buttons
        self.suggest_move_button = self.play_game.suggest_move_button
        self.suggest_move_button.pack(side=tk.LEFT)
        self.play_game.update_suggest_button_state()
        self.transition_sides_button = self.play_game.transition_sides_button
        self.transition_sides_button.config(bg="SystemButtonShadow")
        self.transition_sides_button.pack(side=tk.LEFT)
        self.print_captured_button = tk.Button(self.root, text="Print Captured Pieces", command=lambda: CapturedOutput(self.root, self.play_game.captured_pieces))
        self.print_captured_button.pack(side=tk.LEFT)
        self.board_draw.draw_board()

        # Place pieces on the board
        self.board_draw.update_pieces()

        # Bind click events to the board
        self.canvas.bind("<Button-1>", self.play_game.on_square_click)

        # Creates a button that prints the board state **DEBUG feature old**
        # print_button = tk.Button(self.root, text="Print Board State", command=self.print_board_state)
        # print_button.pack(side=tk.LEFT)

        # Makes it so you can hit Escape to leave the game
        self.root.bind("<Escape>", lambda event: self.game_over.quit_game())
        self.root.bind("<Return>", lambda event : self.play_game.wait_lock.set(1)) # True

        # Makes it so that X-ing out of the application leaves the game
        self.root.protocol("WM_DELETE_WINDOW", self.game_over.quit_game)

        # Draw the inital fog
        self.board_draw.draw_fog()
        
        # Start the chess engine
        self.engine.start_engine()
        
class CapturedOutput(tk.Toplevel):
    """Display the captured pieces for both players."""
    def __init__(self, parent, captured_pieces):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Captured.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(200, 150)
        self.title("Captured Pieces")
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=captured_pieces, wraplength=280).pack(padx=50, pady=5)

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM, padx=10, pady=5)


    def ok(self):
        self.close()
       
    def close(self):
        self.destroy()
        


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("images/icons/FOW.ico")
    app = ChessGUI(root)
    root.mainloop()