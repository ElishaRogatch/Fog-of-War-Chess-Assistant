import tkinter as tk
from tkinter import messagebox
import fow_chess
import sqlite3
from fow_engine import FoW_Engine1
from input_processor import InputProcessor
from board_draw import DrawBoard
from play_game import PlayGame
from database import Database
from game_over import GameOver




class ChessGUI:
    def __init__(self, root):
        self.root = root
        # Initialize MySQL database connection
        self.connection = sqlite3.connect("fogofwar.db")
        self.cursor = self.connection.cursor()
        # initializes board
        self.board = fow_chess.FowBoard()
        self.root.title("Two-Player Chess Game")
        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels
        # Create Canvas to draw chessboard
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        self.canvas.pack()
        # Track whose turn it is (True for white, False for black) and initialize update_suggest_button_state
        self.is_white_turn = True
        # Create an instance of FoW_Engine1, passing the connection
        self.engine = FoW_Engine1(self.connection)
        # initialize GameOver
        self.game_over = GameOver(self.root, self.cursor, self.connection, self.board)
        # make instance of Database
        self.database = Database(self.root, self.board, self.connection, self.cursor)
        # makes instance of DrawBoard
        self.board_draw = DrawBoard(self.root, self.board, self.board_size, self.square_size, self.canvas, self.connection, self.cursor)
        # Create an instance of InputProcessor and set a variable for bias
        self.processor = InputProcessor()  
        self.biases = self.processor.bias()
        # make instance of PlayGame
        self.play_game = PlayGame(self.root, self.board, self.canvas, self.square_size, self.board_draw, self.connection, self.cursor, self.database, self.game_over, self.is_white_turn, self.engine, self.biases)
        self.suggest_move_button = self.play_game.suggest_move_button
        self.suggest_move_button.pack(side=tk.LEFT)
        
        self.play_game.update_suggest_button_state()
        # initilaizes moves
        self.moves = ""
        
        # fill up the board
        self.database.refill_board()
        
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
        # # Create a button to print the moves made in the game
        # self.move_list = []
        # print_moves_button = tk.Button(self.root, text="Print Move History", command=self.database.print_moves)
        # print_moves_button.pack(side=tk.LEFT)
        print_captured_button = tk.Button(self.root, text="Print Captured Pieces", command=self.print_captured_pieces)
        print_captured_button.pack(side=tk.LEFT)
        # ran here once to set up original visibility for player 1
        self.database.update_visibility_white(list(self.board.fow_legal_moves))
        # ran here once to set up original visibility for player 2
        self.database.update_visibility_black(list(self.board.fow_legal_moves))
        # white starts first therefore we run this here
        self.board_draw.draw_fog_white()
    
    def print_captured_pieces(self):
        """Print the captured pieces for both players."""
        captured_list = []
        self.cursor.execute("SELECT * FROM captured;")
        results = self.cursor.fetchall()
        # Print each row to the console
        for row in results:
            print(row[0])  # Prints each row from the database
            captured_list.append(row[0])
        messagebox.showinfo("Captured Peices", captured_list)


    # make this an accessible list throughout code
    def print_legal_moves(self, legal_moves):
        print(legal_moves)
        print(len(legal_moves))

    # debug function
    def print_board_state(self):
        """Print the current board state (for debugging purposes)."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()

        # Print each row to the console
        for row in results:
            print(row)  # Prints each row from the database

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
    
