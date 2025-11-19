import tkinter as tk
from tkinter import messagebox
import fow_chess
from fow_engine import FoW_Engine1
from input_processor import InputProcessor
from board_draw import DrawBoard
from play_game import PlayGame
from game_over import GameOver


class ChessGUI:
    def __init__(self, root):
        self.root = root
        # initializes board
        self.board = fow_chess.FowBoard()
        self.root.title("Two-Player Chess Game")
        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels
        # Create Canvas to draw chessboard
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        self.canvas.pack()
        # Track which player is the assisted one
        self.assisted_player = fow_chess.WHITE
        # makes instance of DrawBoard
        self.board_draw = DrawBoard(self.root, self.board, self.board_size, self.square_size, self.canvas)
        # Create an instance of InputProcessor and set a variable for bias
        self.processor = InputProcessor()  
        self.biases = self.processor.bias()
        # create instance of board state limiter and probable state analyzer
        # Create an instance of FoW_Engine1
        self.engine = FoW_Engine1(self.board, self.biases)
        self.engine.start_engine()
        # initialize GameOver
        self.game_over = GameOver(self.root, self.board, self.engine)
        # make instance of PlayGame
        self.play_game = PlayGame(self.root, self.board, self.canvas, self.square_size, self.assisted_player, self.board_draw, self.game_over, self.engine, self.biases)
        #initialize game buttons
        self.suggest_move_button = self.play_game.suggest_move_button
        self.suggest_move_button.pack(side=tk.LEFT)
        self.play_game.update_suggest_button_state()
        self.transition_sides_button = self.play_game.transition_sides_button
        self.transition_sides_button.config(bg="SystemButtonShadow")
        self.transition_sides_button.pack(side=tk.LEFT)
        self.print_captured_button = tk.Button(self.root, text="Print Captured Pieces", command=self.print_captured_pieces)
        self.print_captured_button.pack(side=tk.LEFT)
        self.board_draw.draw_board()
        # Place pieces on the board
        self.board_draw.update_pieces()
        # Bind click events to the board
        self.canvas.bind("<Button-1>", self.play_game.on_square_click)
        # Creates a button that prints the board state **debug feature**
        # print_button = tk.Button(self.root, text="Print Board State", command=self.print_board_state)
        # print_button.pack(side=tk.LEFT)
        # Makes it so you can hit Escape to leave the game
        self.root.bind("<Escape>", lambda event: self.game_over.quit_game())
        self.root.bind("<Return>", lambda event: self.play_game.wait_lock.set(True))
        # Makes it so that X-ing out of the application leaves the game
        self.root.protocol("WM_DELETE_WINDOW", self.game_over.quit_game)
        # Create a button to print the moves made in the game
        # self.move_list = []
        # print_moves_button = tk.Button(self.root, text="Print Move History", command=self.database.print_moves)
        # print_moves_button.pack(side=tk.LEFT)
        # Draw the inital fog
        self.board_draw.draw_fog()
    
    def print_captured_pieces(self):
        """Print the captured pieces for both players."""
        captured_box = tk.Toplevel()
        captured_box.title("Captured Peices")
        captured_box.geometry("300x150")
        captured_box.grab_set()
        captured_box.iconbitmap("images/icons/Captured.ico")
        tk.Label(captured_box, text=self.play_game.captured_pieces, wraplength=280).pack(pady=(10, 0))
        tk.Button(captured_box, text="OK", command=captured_box.destroy).pack(pady=10,side= tk.BOTTOM)

    # make this an accessible list throughout code
    def print_legal_moves(self, legal_moves):
        print(legal_moves)
        print(len(legal_moves))

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("images/icons/FOW.ico")
    app = ChessGUI(root)
    root.mainloop()