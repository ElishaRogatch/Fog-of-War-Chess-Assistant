from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from probable_state_analyzer import ProbableStateAnalyzer
    from board_state_limiter import BoardStateLimiter

import tkinter as tk
import chess
from board_draw import DrawBoard
import fow_chess


class PredictionWindow(tk.Toplevel):
    def __init__(self, parent, PSA: ProbableStateAnalyzer, BSL: BoardStateLimiter, main_board: fow_chess.FowBoard, assisted_player: chess.Color):
        """Initialize the prediction window."""
        super().__init__(parent)
        self.parent = parent
        self.title("Opponent Move Predictions")
        self.iconbitmap("images/icons/FOW.ico")
        
        # Store references to the PSA and BSL for accessing predictions and board states
        self.PSA = PSA
        self.BSL = BSL
        self.main_board = main_board
        
        # Store reference to assisted player
        self.assisted_player = assisted_player

        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels


        # Create a canvas to display predictions 
        self.canvas = tk.Canvas(self, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        
        # Global variable to track visibility of the prediction window
        self.isVisible = False

        # Frame to hold the buttons for switching predictions
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Lists to store button objects and images 
        self.buttons = [] # [Prediction 1, Prediction 2, Prediction 3, Prediction 4, Prediction 5, Compiled Prediction, Toggle bp vision, Toggle br vision, Toggle bn vision, Toggle bb vision, Toggle bq vision, Toggle bk vision]
        self.button_images = []
        if self.assisted_player == chess.WHITE:
            self.piece_names = ["bp", "bn", "bb", "br", "bq", "bk"] 
        else:
            self.piece_names = ["wp", "wn", "wb", "wr", "wq", "wk"] 
        self.initialize_percentages() # This will be used to store the percentage frequencies of pieces on tiles across all predicted board states for use in drawing outlines on the prediction board based on piece frequency in the predictions

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
        self.psa_predictions = self.PSA.board_scores[:5] # This is a list of the 5 most probable board states from the PSA, which will be used to switch between predictions

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
        #self.prediction_board = fow_chess.FowBoard() # This will be updated with the predicted board state (DO WE NEED THIS ?? Answer: Not really as we update the board stored inside the DrawBoard instance, updating this does not update the drawn board)
        self.compiled_prediction_board = fow_chess.FowBoard() # This will be updated with the compiled prediction and piece vision toggles
        self.compiled_prediction_board_copy = self.compiled_prediction_board.copy() # Copy for safe modification when updating the compiled prediction based on piece vision toggles
        self.prediction_board_draw = DrawBoard(self, fow_chess.FowBoard(), self.board_size, self.square_size, self.canvas)
        self.prediction_board_draw.set_prediction_window(self) # Pass the prediction window instance to the board draw class
        self.create_compiled_prediction() # Create the initial compiled prediction based on the initial predictions from the PSA and the current piece vision toggles (which are all off at the start)

        # Use the DrawBoard instance to draw the initial prediction board and pieces
        self.prediction_board_draw.draw_board()
        self.prediction_board_draw.update_pieces()
        self.canvas.pack()

    # ------- Functions for Updating Predictions --------
    def update_predictions(self, board_states: list):
        """Update the predictions stored in the PSA predictions list and the corresponding buttons, as well as the compiled prediction."""
        # NOTE: This function is called in the PlayGame class when new predictions are generated by the PSA after each move
        self.psa_predictions = board_states[:5] # Keep only the 5 most probable predictions from the PSA
        self.create_compiled_prediction() # Update the compiled prediction based on the new predictions and current piece vision toggles

        # If the currently active prediction index is greater than the number of available predictions, reset it to 0
        if self.active_prediction >= len(self.psa_predictions):
            self.active_prediction = 0
            self.active_piece_vision = None
        
        # Then update the prediciton board buttons
        self.enable_disable_prediction_buttons()
        self.update_prediction_buttons()
        self.enable_disable_piece_vision_buttons()
        self.update_piece_vision_buttons()

        self.update_prediction_board(self.psa_predictions[self.active_prediction][0])        

    def update_prediction_board(self, board_index: int):
        """Update the drawn board to reflect the board state of the selected prediction index."""
        self.prediction_board_draw.board = self.BSL.board_states[board_index]
        self.prediction_board_draw.update_pieces()

    def update_compiled_prediction(self, compiled_board_state: fow_chess.FowBoard):
        """Update the drawn board to reflect the compiled prediction state."""
        self.prediction_board_draw.board = compiled_board_state
        self.prediction_board_draw.update_outlines()

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
        """Enable or disable the prediction buttons based on the current PSA predictions."""
        # This function will be implemented to enable/disable buttons based on the availability of predictions and update button images if necessary
        for i in range(5):
            if i < len(self.psa_predictions):
                self.buttons[i].config(state=tk.NORMAL)
            else:
                self.buttons[i].config(state=tk.DISABLED)

        self.buttons[5].config(state=tk.NORMAL) # The compiled prediction button is always enabled

    def update_prediction_buttons(self):
        """Update the configurations of the prediction buttons based on the current prediction index."""
        for i in range(6):
            if i == self.active_prediction:
                self.buttons[i].config(relief="sunken", bg="SystemButtonShadow")
            else:
                self.buttons[i].config(relief="raised", bg="SystemButtonFace")

    def enable_disable_piece_vision_buttons(self):
        """Enable or disable the piece vision buttons based on the current selected prediction."""
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
            self.withdraw()  # Hide the window
        else:
            self.deiconify()  # Show the window

        self.isVisible = not self.isVisible # Flip the boolean value for next toggle

    def switch_to_prediction(self, index: int):
        """Switch the displayed prediction based on the index."""
        # Update the active prediction index and button configurations
        self.active_prediction = index
        self.update_prediction_buttons()

        # If the compiled prediction is selected, update the prediction board to the compiled prediction board
        if self.active_prediction == 5: 
            self.update_compiled_prediction(self.compiled_prediction_board)
        else:
            # Update the prediction board to the board state of the selected prediction and update the drawn board
            self.update_prediction_board(self.psa_predictions[self.active_prediction][0])      

        # Enable or disable piece vision toggle buttons based on whether the compiled prediction is active  
        self.enable_disable_piece_vision_buttons()         

    def toggle_specific_piece_vision(self, piece_type: str):
        """Toggle the vision of a specific piece type in the compiled prediction."""
        isSwitching = self.active_piece_vision is not None and self.active_piece_vision != piece_type # Check if we are switching to a different piece vision from a currently toggled piece vision
        isFirstToggle = self.active_piece_vision is None # Check if this is the first piece vision being toggled on
        isUntoggling = self.active_piece_vision == piece_type # Check if we are toggling off the current piece vision

        # Update the active piece vision based on the toggle and update button configurations
        if self.active_piece_vision == piece_type:
            self.active_piece_vision = None
        else:
            self.active_piece_vision = piece_type
        self.update_piece_vision_buttons()
        
        # Remove all pieces from the compiled prediction board that are not the currently toggled piece type, then update the prediction board draw to reflect the changes in piece vision
        if isFirstToggle:
            self.compiled_prediction_board_copy = self.compiled_prediction_board.copy() # Make a copy of the current compiled prediction boardbefore modifying
            self.remove_other_pieces(piece_type) 
            self.add_low_percentage_pieces(piece_type) # Add back pieces of the toggled piece type that were removed based on low frequency in the predictions, so that they are visible when toggling on that piece vision
        elif isSwitching:
            self.compiled_prediction_board = self.compiled_prediction_board_copy.copy() # Start with a fresh copy of the compiled prediction board to remove pieces from based on the piece vision toggle
            self.remove_other_pieces(piece_type)
            self.add_low_percentage_pieces(piece_type) # Add back pieces of the toggled piece type that were removed based on low frequency in the predictions, so that they are visible when toggling on that piece vision
        elif isUntoggling:
            self.compiled_prediction_board = self.compiled_prediction_board_copy.copy() # If toggling off the current piece vision, reset to the saved copy

        # After updating the compiled prediction board based on the piece vision toggles, update the prediction board to reflect the changes and update the drawn board
        self.update_compiled_prediction(self.compiled_prediction_board)

    def remove_other_pieces(self, piece_type: str):
        """Remove pieces that are not the specified piece type from the compiled prediction board."""
        # Loop through the squares on the board
        for tile in chess.SQUARES:
            piece = self.compiled_prediction_board.piece_at(tile)
            if piece is not None and piece.color != self.assisted_player: # Only consider opponent pieces for the predictions
                if chess.PIECE_SYMBOLS[piece.piece_type] == piece_type[1]: # If the piece type matches the toggled piece type, set it on the compiled prediction board, otherwise remove it from the compiled prediction board
                    self.compiled_prediction_board.set_piece_at(tile, piece)
                else:
                    self.compiled_prediction_board.remove_piece_at(tile)

    def add_low_percentage_pieces(self, piece_type: str):
        """Add pieces of the specified piece type back to the compiled prediction board if their frequency percentage across all boards is greater than 0."""
        # Loop through the squares on the board
        for tile in chess.SQUARES:
            self.piece_counts[tile] = self.piece_counts.get(tile, [0]*6) # Get the piece counts for the tile, default to [0]*6 if not found
            piece_index = self.piece_names.index(piece_type) # Get the index of the piece type in the piece names list to access the corresponding count in the piece counts
            count = self.piece_counts[tile][piece_index] # Get the count of the toggled piece type on the tile across all predicted board states
            if count > 0: # If the piece is present on at least one predicted board state, add it back to the compiled prediction board so that it is visible when toggling on the piece vision
                self.compiled_prediction_board.set_piece_at(tile, chess.Piece(piece_index + 1, not self.assisted_player)) # Piece types are 1-indexed in the piece counts list, so add 1 to get the actual piece type and set it on the compiled prediction board
 
    # --------- Compiled Prediction Creation and Updating ---------
    def create_compiled_prediction(self):
        """Create a dictionary to be used for the compiled prediction board based on the current piece vision toggles."""
        # Remove all pieces before adding pieces based on frequency in the predictions
        self.compiled_prediction_board.clear_board() 

        # Initialize the piece frequency dictionary with empty lists for each tile
        piece_counts = {tile : [0] * 6 for tile in chess.SQUARES}  # Format: {tile : counts[count_pawns, count_knights, count_bishops, count_rooks, count_queens, count_kings]}

        # Initialize storage for calculating the sum of all weights to determine percentage later
        self.weighted_score_sum = 0

        # Loop through each (index, score) tuple in the PSA output and count the frequency of each piece type on each tile across all board states, storing the pieces in the piece_freq dictionary
        for boardTuple in self.PSA.board_scores:
            boardIndex = boardTuple[0] # Retrieve index of board from PSA
            board = self.BSL.board_states[boardIndex] # Retrieve board using index
            score = boardTuple[1] # Retrieve score from PSA 
            shifted = score + 10000 # Shift all scores to be positive
            normalized = shifted / 20000 # Normalize all scores to be on scale from 0 to 1 
            weight = normalized ** 3 # Bias strongly towards the higher scores 
            self.weighted_score_sum += weight # Keep track of sum of all weights

            # Loop through each tile of each board and calculate the frequency of each piece types on each tile adding the weight to bias towards better scoring boards
            for tile in chess.SQUARES:
                piece = board.piece_at(tile)
                if piece and piece.color != self.assisted_player: # Only consider opponent pieces for the predictions
                    piece_counts[tile][piece.piece_type - 1] += weight # Piece types are 1:pawn, 2:knight, 3:bishop, 4:rook, 5:queen, 6:king 

        self.piece_counts = piece_counts # Store the piece counts for use in the piece vision toggle function to determine whether to add back pieces that were removed based on low frequency
        self.create_compiled_prediction_board(piece_counts) # Create the compiled prediction board based on the frequency of pieces in the predictions and the current piece vision toggles
        self.add_back_pieces() # Add back assisted players pieces to the compiled prediction board based on the current board state, since the predictions only concern the opponent's pieces

    def create_compiled_prediction_board(self, piece_counts: dict):
        """Create a compiled prediction board based on the frequency of pieces in the predictions and the current piece vision toggles."""
        for tile, counts in piece_counts.items():
            total_pieces = sum(counts) # Total of all types of pieces on the current tile across all predicted board states          

            # Calculate and add the percentage for each type of piece on the current tile
            percentage = [(count / self.weighted_score_sum)*100 for count in counts] # Calculate the percentage frequency of each piece type on the tile across all predicted board states when there are multiple piece types on the current tile (Needs to be accessed by board draw to draw the correct outlines.)
            self.percentages[tile] = percentage

            # Using total pieces on the current tile across all predictions, determine which piece to show on the compiled prediction board 
            if total_pieces == 0:
                continue  # No non assisted player pieces predicted on this tile

            # Pick the most frequent piece
            piece_type = counts.index(max(counts)) + 1 # Piece types are 1-indexed in the counts list, so add 1 to get the actual piece type
            self.compiled_prediction_board.set_piece_at(tile, chess.Piece(piece_type, not self.assisted_player)) # Update the board with the piece
        
        #for tile in chess.SQUARES:
        #    print(f"Tile {chess.square_name(tile)}: Percentages {self.percentages[tile]}") # DEBUG print to check the calculated percentages for each tile

    def add_back_pieces(self):
        """Add back assisted players pieces to the compiled prediction board based on the current board state, since the predictions only concern the opponent's pieces."""
        for tile in chess.SQUARES:
            piece = self.main_board.piece_at(tile) # Check the current board state for assisted players pieces to add back to the compiled prediction board
            if piece and piece.color == self.assisted_player:
                self.compiled_prediction_board.set_piece_at(tile, piece) # Add back the players piece to the compiled prediction board
    
    def initialize_percentages(self):
        """Initialize the percentages dictionary with 0% for all piece types on all tiles."""
        self.percentages = {tile : [0] * 6 for tile in chess.SQUARES}  # Format: {tile : percentages[percentage_pawns, percentage_knights, percentage_bishops, percentage_rooks, percentage_queens, percentage_kings]} 