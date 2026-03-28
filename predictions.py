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
        self.prediction_window_root = tk.Toplevel(root)
        self.prediction_window_root.title("Opponent Move Predictions")

        # Create a canvas to display predictions 
        self.canvas = tk.Canvas(self.prediction_window_root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        
        # Global variable to track visibility of the prediction window
        self.isVisible = False

        # Frame to hold the buttons for switching predictions
        self.button_frame = tk.Frame(self.prediction_window_root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Lists to store button objects and images 
        self.buttons = [] # [Prediction 1, Prediction 2, Prediction 3, Prediction 4, Prediction 5, Compiled Prediction, Toggle bp vision, Toggle br vision, Toggle bn vision, Toggle bb vision, Toggle bq vision, Toggle bk vision]
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

        # Store PSA output for the 5 most probable states and the compiled prediction
        self.psa_predictions = [self.PSA.board_scores[:5]] # This is a list of the 5 most probable board states from the PSA, which will be used to switch between predictions

        # Create the buttons based on the configs
        self.create_buttons()

        # Update the configs of the prediction buttons
        self.enable_disable_prediction_buttons()
        self.active_prediction = 0  # This variable will track which prediction is currently being displayed, so the corresponding button can be highlighted
        self.update_prediction_buttons()

        # Update the configs of the piece vision toggle buttons
        self.enable_disable_piece_vision_buttons()
        self.active_piece_vision = None # This variable will track which piece vision is currently toggled, so the corresponding button can be highlighted
        self.update_piece_vision_buttons()

        # Store other variables for predictions and piece vision states
        self.prediction_board = fow_chess.FowBoard() # This will be updated with the predicted board state
        self.compiled_prediction_board = fow_chess.FowBoard() # This will be updated with the compiled prediction and piece vision toggles
        self.prediction_board_draw = DrawBoard(self.prediction_window_root, self.prediction_board, self.board_size, self.square_size, self.canvas)

        # Use the DrawBoard instance to draw the initial prediction board and pieces
        self.prediction_board_draw.draw_board()
        self.prediction_board_draw.update_pieces()
        self.canvas.pack()

    # ------- Functions for Updating Predictions --------
    def update_predictions(self, board_states):
        """Update the predictions stored in the PSA predictions list and the corresponding buttons."""
        print("Updating predictions in PredictionWindow...")
        self.psa_predictions = board_states
        self.enable_disable_prediction_buttons()

        # If the currently active prediction index is greater than the number of available predictions, reset it to 0
        if self.active_prediction >= len(self.psa_predictions):
            self.active_prediction = 0
        
        # Then update the prediciton board
        self.update_prediction_buttons()
        self.update_prediction_board(self.psa_predictions[self.active_prediction][0])
        

    def update_prediction_board(self, board_index):
        self.prediction_board_draw.board = self.BSL.board_states[board_index]
        self.prediction_board_draw.update_pieces()

    def update_compiled_prediction(self, compiled_board_state):
        pass

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

    def enable_disable_prediction_buttons(self):
        """Update the configurations of the prediction buttons based on the current PSA predictions."""
        # This function will be implemented to enable/disable buttons based on the availability of predictions and update button images if necessary
        for i in range(6):
            if i < len(self.psa_predictions):
                self.buttons[i].config(state=tk.NORMAL)
            else:
                self.buttons[i].config(state=tk.DISABLED)

    def update_prediction_buttons(self):
        """Update the configurations of the prediction buttons based on the current prediction index."""
        for i in range(6):
            if i == self.active_prediction:
                self.buttons[i].config(relief="sunken", bg="SystemButtonShadow")
            else:
                self.buttons[i].config(relief="raised", bg="SystemButtonFace")

    def enable_disable_piece_vision_buttons(self):
        """Update the configurations of the piece vision buttons based on the current PSA predictions."""
        # This function will be implemented to enable/disable buttons based on whether the compiled prediction is active and update button images if necessary
        if self.active_prediction == 5: # If the compiled prediction is active, enable all piece vision toggle buttons, otherwise disable them
            for i in range(6, 12):
                self.buttons[i].config(state=tk.NORMAL)
        else:
            for i in range(6, 12):
                self.buttons[i].config(state=tk.DISABLED)

    def update_piece_vision_buttons(self):
        """Update the configurations of the piece vision buttons based on the current piece vision toggled."""
        # This function will be implemented to update the button configurations based on the current piece vision toggled
        for i in range(6, 12):
            piece_type = self.piece_names[i-6]
            if self.active_piece_vision == piece_type:
                self.buttons[i].config(relief="sunken", bg="SystemButtonShadow")
            else:
                self.buttons[i].config(relief="raised", bg="SystemButtonFace")

    # ------------- Button Command Functions -------------
    def toggle(self):
        """Toggle the visibility of the prediction window."""
        if self.isVisible:
            self.prediction_window_root.withdraw()  # Hide the window
        else:
            self.prediction_window_root.deiconify()  # Show the window

        self.isVisible = not self.isVisible # Flip the boolean value for next toggle

    def switch_to_prediction(self, index):
        """Switch the displayed prediction based on the index."""
        # Update the active prediction index and button configurations
        self.active_prediction = index
        self.update_prediction_buttons()

        # Update the prediction board to the board state of the selected prediction and update the drawn board
        self.update_prediction_board(self.psa_predictions[self.active_prediction][0])      

        # Enable or disable piece vision toggle buttons based on whether the compiled prediction is active  
        self.enable_disable_piece_vision_buttons()         

        # Still needs special case for compiled prediction !!!

    def toggle_specific_piece_vision(self, piece_type):
        """Toggle the vision of a specific piece type in the predictions."""
        # Still needs to remove the pieces not selected from the compiled prediction board and update the prediction board draw to reflect the changes in piece vision
        if self.active_piece_vision == piece_type:
            self.active_piece_vision = None
        else:
            self.active_piece_vision = piece_type
        self.update_piece_vision_buttons()

    def create_compiled_prediction(self):
        """Create a compiled prediction board based on the current piece vision toggles."""
        # This function will be implemented to compile the prediction boards from the BSL
        pass