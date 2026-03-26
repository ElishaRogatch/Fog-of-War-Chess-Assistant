import tkinter as tk
from board_draw import DrawBoard
import fow_chess
from probable_state_analyzer import ProbableStateAnalyzer
from board_state_limiter import BoardStateLimiter

class PredictionWindow:
    def __init__(self, root, PSA: ProbableStateAnalyzer, BSL: BoardStateLimiter):
        """Initialize the prediction window."""
        # Store references to the PSA and BSL for accessing predictions and board states
        self.PSA = PSA
        self.BSL = BSL

        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels

        # Create a new Toplevel window for predictions
        self.prediction_window = tk.Toplevel(root)
        self.prediction_window.title("Opponent Move Predictions")

        # Create a canvas to display predictions 
        self.canvas = tk.Canvas(self.prediction_window, width=self.board_size * self.square_size, height=self.board_size * self.square_size)

        # Global variable to track visibility of the prediction window
        self.isVisible = False

        # Frame to hold the buttons for switching predictions
        self.button_frame = tk.Frame(self.prediction_window)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Lists to store button objects and images 
        self.buttons = []
        self.button_images = []
        self.piece_names = ["bp", "br", "bn", "bb", "bq", "bk"]

        # Configuration for the buttons
        self.button_configs = [
            {"text": "1", "command" : (lambda: self.switch_to_prediction(0))},
            {"text": "2", "command" : (lambda: self.switch_to_prediction(1))},
            {"text": "3", "command" : (lambda: self.switch_to_prediction(2))},
            {"text": "4", "command" : (lambda: self.switch_to_prediction(3))},
            {"text": "5", "command" : (lambda: self.switch_to_prediction(4))},
            {"text": "C", "command" : (lambda: self.switch_to_prediction(5))},
        ]

        # Add in the configs for buttons that use images instead of text
        for piece in self.piece_names:
            image = tk.PhotoImage(file=f"images/pieces/{piece}.png")
            self.button_images.append(image)
            self.button_configs.append({"image": image, "command": (lambda p=piece: self.toggle_specific_piece_vision(p))})

        # Create the buttons based on the configs
        self.create_buttons()

        # Store other variables for predictions and piece vision states
        self.prediction_board = fow_chess.FowBoard() # This will be updated with the predicted board state
        self.compiled_prediction_board = fow_chess.FowBoard() # This will be updated with the compiled prediction and piece vision toggles
        self.prediction_board_draw = DrawBoard(self.prediction_window, self.prediction_board, self.board_size, self.square_size, self.canvas)

        # Use the DrawBoard instance to draw the initial prediction board (need to initialize the list of predictions from the PSA here as well)
        self.prediction_board_draw.draw_board()
        self.prediction_board_draw.update_pieces()
        self.canvas.pack()

        # Store PSA output for the 5 most probable states and the compiled prediction
        self.psa_predictions = [self.PSA.board_scores[:5]] # This is a list of the 5 most probable board states from the PSA, which will be used to switch between predictions

    # ------- Button Creation and Configuration --------
    def create_buttons(self):
        """Create buttons from list of configs for switching predictions and toggling piece vision."""
        for i, config in enumerate(self.button_configs):
            row = i // 6
            col = i % 6

            button_kwargs = {"command": config["command"],}

            if "text" in config:
                button_kwargs["text"] = config["text"]
            if "image" in config:
                button_kwargs["image"] = config["image"]
        
            button = tk.Button(self.button_frame, **button_kwargs)
            button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew") # Use grid for better control over button placement and resizing
            self.buttons.append(button)
        
        # Configure grid weights for even button distribution when resized
        for col in range(6):
            self.button_frame.grid_columnconfigure(col, weight=1)
        for row in range(2):
            self.button_frame.grid_rowconfigure(row, weight=1)

    # ------------- Button Functions -------------
    def toggle(self):
        """Toggle the visibility of the prediction window."""
        if self.isVisible:
            self.prediction_window.withdraw()  # Hide the window
        else:
            self.prediction_window.deiconify()  # Show the window

        self.isVisible = not self.isVisible # Flip the boolean value for next toggle

    def switch_to_prediction(self, index):
        """Switch the displayed prediction based on the index."""
        # This function will be implemented to update the canvas with the selected prediction
        pass

    def toggle_specific_piece_vision(self, piece_type):
        """Toggle the vision of a specific piece type in the predictions."""
        # This function will be implemented to update the compiled prediction based on the passed piece type
        pass

    def create_compiled_prediction(self):
        """Create a compiled prediction board based on the current piece vision toggles."""
        # This function will be implemented to compile the prediction boards from the BSL
        pass