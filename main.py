from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import chess

import tkinter as tk
import fow_chess
from fow_engine import FowEngine
from input_processor import InputProcessor
from board_draw import DrawBoard
from play_game import PlayGame
from game_over import GameOver
from fow_logger import FowLogger
from pathlib import Path
from gui_io import MessageOutput
from game_settings import GameSettings, SettingsManager

from predictions import PredictionWindow

class ChessGUI:
    def __init__(self, root, names: list[str], settings: GameSettings):
        """Initialize the main GUI application."""
        self.root = root
        self.root.title("Two-Player Fog Of War Chess Game")
        self.settings = settings

        # Initializes board
        self.board = fow_chess.FowBoard()

        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels

        # Create Canvas to draw chessboard
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        self.canvas.pack()

        # Track which player is the assisted one
        self.assisted_player: chess.Color = self.settings.assisted_player
        
        # Player names
        self.names = names # Names in list are black then white so that it can be accesed through the turn property

        # Makes instance of FowLogger
        self.logger = FowLogger(self.settings)
        self.logger.log(f"Game started between {names[1]} and {names[0]}")

        # Makes instance of DrawBoard
        self.board_draw = DrawBoard(self.root, self.board, self.board_size, self.square_size, self.canvas)

        # Create an instance of InputProcessor and set a variable for bias
        self.processor = InputProcessor(self.root, self.logger)  
        self.biases = self.processor.bias()

        # Initialize GameOver
        self.game_over = GameOver(self.root, self.board, self.logger, self.names)

        # Create an instance of FowEngine
        self.engine = FowEngine(self.root, self.board, self.biases, self.game_over, self.logger, self.settings)
        self.game_over.assign_engine(self.engine)

        # Make instance of PlayGame
        self.play_game = PlayGame(self.root, self.board, self.canvas, self.square_size, self.assisted_player, self.board_draw, self.game_over, self.engine, self.biases, self.logger, self.names, self.settings)

        # Initialize game buttons
        self.suggest_move_button = self.play_game.suggest_move_button
        self.suggest_move_button.pack(side=tk.LEFT)
        self.play_game.update_suggest_button_state()
        self.transition_sides_button = self.play_game.transition_sides_button
        self.transition_sides_button.pack(side=tk.LEFT)
        self.print_captured_button = tk.Button(self.root, text="Print Captured Pieces", command=lambda: self.captured_message(self.play_game.captured_pieces))
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
        self.root.bind("<Escape>", lambda event: self.game_over.force_quit_gamequit_game())
        self.root.bind("<Return>", lambda event : self.play_game.wait_lock.set(1)) # True

        # Makes it so that X-ing out of the application leaves the game
        self.root.protocol("WM_DELETE_WINDOW", self.game_over.force_quit_game)

        # Draw the inital fog
        self.board_draw.draw_fog()
        
        # Start the chess engine
        self.engine.start_engine()
    
        # Create the prediction window via the prediction class and pass the root
        self.prediction_window = PredictionWindow(self.root, self.play_game.PSA, self.play_game.BSL, self.board) 

        def toggle_predictions():
            self.prediction_window.toggle()
            # Change the button color based on the visibility of the prediction window
            if self.prediction_window.isVisible:
                self.toggle_predictions_button.config(relief="sunken", bg="SystemButtonShadow") # Shadow when toggled on
            else:
                self.toggle_predictions_button.config(relief="raised", bg="SystemButtonFace") # Light when toggled off     

        # Override the close button to toggle visibility instead of destroying the window
        self.prediction_window.protocol("WM_DELETE_WINDOW", toggle_predictions)

        # Create a button to toggle the prediction window
        self.toggle_predictions_button = tk.Button(self.root, text="Toggle Predictions", command=toggle_predictions)
        self.toggle_predictions_button.config(bg="SystemButtonFace")
        self.toggle_predictions_button.pack(side=tk.LEFT)

        self.play_game.set_prediction_window(self.prediction_window, self.toggle_predictions_button) # Pass the prediction window instance to the play game class    

        # Re-hide the prediction window on startup
        self.prediction_window.withdraw()    
    def captured_message(self, captured_pieces):
        """Display the captured pieces for both players."""
        return MessageOutput(
            parent=self.root,
            message=captured_pieces,
            title="Captured Pieces",
            icon_path="images/icons/Captured.ico",
            wrap_length=280,
            label_font=("TkDefaultFont", 30),
            label_padding=(50,5)
        )
        

        
class MainMenu(tk.Toplevel):
    """Display the Main menu for the game."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/FOW.ico")
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.minsize(200, 150)
        self.title("Two-Player Fog Of War Chess Game")
        self.result = False
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        # Buttons
        tk.Button(self, text="Quit", command=self.quit).pack(side=tk.BOTTOM, padx=10, pady=5)
        tk.Button(self, text="Settings", command=self.settings).pack(side=tk.BOTTOM, padx=10, pady=5)
        tk.Button(self, text="Play Game", command=self.play_game).pack(side=tk.BOTTOM, padx=10, pady=5)
        
        
        # Pauses code until answered
        self.wait_window(self)


    def play_game(self):
        self.result = True
        self.names = PlayerInput(self).names
        self.close()
        
    def settings(self):
        SettingsManager(self)
        
    def quit(self): # Result is false by default
        self.close()
       
    def close(self):
        self.destroy()
        
class PlayerInput(tk.Toplevel):
    """Display the input asking players to enter their names."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/FOW.ico")
        self.protocol("WM_DELETE_WINDOW", self.ok)
        self.minsize(200, 100)
        self.title("Name Input")
        self.first_entry = True
        self.names = ["", ""]
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        self.label = tk.Label(self, text= "Enter the name of player 1")
        self.label.pack(padx=30, pady=(15,15))
        
        self.name_entry = tk.Entry(self, width=24) # Entry box to type player name
        self.name_entry.pack(padx=10, pady=5)

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM, padx=10, pady=5)

        # Pauses code until answered
        self.wait_window(self)


    def ok(self):
        if self.first_entry:
            name1 = self.name_entry.get()
            if name1:
                self.names[1] = name1
            else:
                self.names[1] = "White"
            self.label.config(text="Enter the name of player 2")
            self.name_entry.delete(0, tk.END)
            self.first_entry = False
        else: # Second entry
            name2 = self.name_entry.get()
            if name2:
                self.names[0] = name2
            else:
                self.names[0] = "Black"
            self.close()
        
    def close(self):
        self.destroy()
        
        


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("images/icons/FOW.ico")
    root.withdraw()
    if not Path("settings.ini").exists():
        SettingsManager.create_default()
    app_menu = MainMenu(root)
    if app_menu.result:
        root.deiconify()
        app = ChessGUI(root, app_menu.names, GameSettings())
        root.mainloop()