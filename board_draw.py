from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_chess import FowBoard

import chess
from chess import Bitboard, BB_SQUARES
import tkinter as tk

class DrawBoard:
    def __init__(self, root, board: FowBoard, board_size: int, square_size: int, canvas: tk.Canvas):
        self.root = root

        # Chess board size
        self.board_size = board_size
        self.square_size = square_size
        self.board = board

        # Create Canvas to draw chessboard
        self.canvas = canvas

        # Load piece images
        self.piece_images = self.load_piece_images()

        # Load outline images for frequency indicators
        self.outline_images = self.load_outline_images()

        # Track dots for move indicators
        self.move_dots = []

    def set_prediction_window(self, prediction_window):
        """Set the prediction window instance to access the percentage frequencies for drawing outlines."""
        self.prediction_window = prediction_window

    def load_piece_images(self) -> dict[str, tk.PhotoImage]:
        """Load piece images from files (you can use any chess piece images here by replacing the .png files in the 'pieces' folder)."""
        pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "wu", "bp", "br", "bn", "bb", "bq", "bk", "bu", "x"]
        piece_images: dict[str, tk.PhotoImage] = {}
        for piece in pieces:
            piece_images[piece] = tk.PhotoImage(file=f"images/pieces/{piece}.png")
        return piece_images
    
    def load_outline_images(self):
        outlines = ["bp", "br", "bn", "bb", "bq", "bk","wp", "wr", "wn", "wb", "wq", "wk"]
        outline_images = {}
        for outline in outlines:
            for color in ["red", "yellow", "green"]:
                outline_images[f"{outline}_outline_{color}"] = tk.PhotoImage(file=f"images/outlines/{outline}_outline_{color}.png")
        return outline_images

    def draw_board(self):
        """Draw the chessboard on the canvas."""
        colors = ["#d6c0a8", "#51361a"]  # Light and dark squares
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = colors[(row + col) % 2]
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        # Add column labels (A-H) at the top and bottom
        for col in range(self.board_size):
            letter = chr(65 + col)
    
            # Top labels
            x_top = col * self.square_size + self.square_size // 1.2
            y_top = self.square_size // 4  # Place near the top edge
            self.canvas.create_text(x_top, y_top, text=letter, font=("Comic Sans MS", 7), fill="black", anchor="s")
    
            # Bottom labels
            x_bottom = col * self.square_size + self.square_size // 1.09
            y_bottom = self.board_size * self.square_size - self.square_size // 4  # Place near the bottom edge
            self.canvas.create_text(x_bottom, y_bottom, text=letter, font=("Comic Sans MS", 7), fill="black", anchor="n")
    
        # Add row labels (1-8)
        for row in range(self.board_size):
            number = str(self.board_size - row)  # Reverse order for chessboard
            x = self.square_size // 4  # Adjust to position inside the board area
            y = row * self.square_size + self.square_size // 5
            self.canvas.create_text(x, y, text=number, font=("Comic Sans MS", 7), fill="black", anchor="e")

    def update_pieces(self):
        """Place pieces on the board according to the current board state."""
        # Clear all existing pieces from the board
        self.canvas.delete("outline")
        self.canvas.delete("piece")

        # Place pieces on the board
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_str = piece.symbol().lower() if piece.color else piece.symbol()
                    image = self.piece_images[f"{'w' if piece.color else 'b'}{piece_str.lower()}"]
                    x = col * self.square_size
                    y = row * self.square_size
                    self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, image=image, tags="piece")
    
    def update_outlines(self):
        """Update the outlines on the pieces based on move frequencies."""
        # Clear existing outlines
        self.canvas.delete("piece")
        self.canvas.delete("outline")

        # Add outline images in place of piece images based on the percentage frequencies from the prediction window
        for row in range(8):
            for col in range(8):
                tile = chess.square(col, 7 - row)
                piece = self.board.piece_at(tile)
                if piece:
                    # Determine the color of the outline based on the percentage frequency of the piece type on the current tile from the prediction window
                    index = piece.piece_type - 1 # Get the index for the piece type (0-5 for pawn to king)
                    percentage = self.prediction_window.percentages[tile][index] # Get the percentage for the piece type on the current tile
                    color = self.get_outline_color(percentage) # Determine the color of the outline based on the percentage
                    piece_str = piece.symbol().lower() # Get the piece symbol in lowercase (e.g., 'p', 'r', 'n', etc.)
                    if color:
                        print(f"{'w' if piece.color else 'b'}{piece_str}_outline_{color}")
                        outline_image = self.outline_images.get(f"{'w' if piece.color else 'b'}{piece_str}_outline_{color}") # Get the corresponding outline image based on the piece type and color
                        if outline_image:
                            pass
                        else:
                            print("SOMETHING WENT WRONG!!!")
                    else:
                        outline_image = self.piece_images.get(f"{'w' if piece.color else 'b'}{piece_str}") # If no outline, just show the piece image (includes white pieces)
                    if outline_image:
                        x = col * self.square_size
                        y = row * self.square_size
                        self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, image=outline_image, tags="outline")

    def get_outline_color(self, percentage):
        """Determine the color of the outline based on the percentage frequency."""
        # Confidences: No Outline - 100%, Green - 70%-99%, Yellow - 36%-69%, Red - 0%-35%  
        if percentage >= 70 and percentage < 100:
            return "green"
        elif percentage >= 36 and percentage < 70:
            return "yellow"
        elif percentage > 0 and percentage < 36:
            return "red"
        else:
            return None
        
    def draw_fog(self):
        """Draws a fog overlay on squares that aren't visible to the white player."""
        # Clear any previous fog overlay
        self.canvas.delete("fog")
        
        # Define the fog color
        fog_color = "#808080"

        # Get visibility bitboard and draw fog on non-visible squares
        visibility: Bitboard = self.board.get_fow_visibility()
        #For each square that is not visible
        for square in chess.scan_forward(~visibility & chess.BB_ALL): #(since python ints arent int64 you have to bring ~visibility into the 64bit domain)
            col = square % 8
            row = (square - col) / 8
            # Calculate the pixel coordinates for the square; 8x8 board with A1 at bottom-left
            x1 = col * self.square_size
            y1 = (7 - row) * self.square_size  
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            
            # Draw a fog rectangle over the square
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fog_color, tags="fog")

        # Redraw column labels (A-H) at the top and bottom that are hidden by fog
        for col in range(self.board_size):
            letter = chr(65 + col)
            if ~visibility & BB_SQUARES[56 + col] and not self.board.turn:
                # Top labels
                x_top = col * self.square_size + self.square_size // 1.2
                y_top = self.square_size // 4  # Place near the top edge
                self.canvas.create_text(x_top, y_top, text=letter, font=("Comic Sans MS", 7), fill="white", anchor="s", tags="fog")
    
            if ~visibility & BB_SQUARES[col] and self.board.turn:
                # Bottom labels
                x_bottom = col * self.square_size + self.square_size // 1.09
                y_bottom = self.board_size * self.square_size - self.square_size // 4  # Place near the bottom edge
                self.canvas.create_text(x_bottom, y_bottom, text=letter, font=("Comic Sans MS", 7), fill="white", anchor="n", tags="fog")

        # Redraw row labels (1-8) that are hidden by fog
        for row in range(self.board_size):
            if ~visibility & BB_SQUARES[8 * (self.board_size - row - 1)]:
                number = str(self.board_size - row)  # Reverse order for chessboard
                x = self.square_size // 4  # Adjust to position inside the board area
                y = row * self.square_size + self.square_size // 5
                self.canvas.create_text(x, y, text=number, font=("Comic Sans MS", 7), fill="white", anchor="e", tags="fog")

        # Show implied piece hints (pieces with location known but not visible under fog)
        for square in chess.scan_forward(self.board.get_semi_visibility(visibility)):
            col = square % 8
            row = (square-col) / 8
            if self.board.occupied & BB_SQUARES[square]:   
                image = self.piece_images[f"{'b' if self.board.turn else 'w'}u"]
            else:
                image = self.piece_images["x"]
            x = col * self.square_size
            y = (7 - row) * self.square_size  
            self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, image=image, tags="fog")

        # Ep pieces (En-Passant target pieces)
        for square in chess.scan_forward(self.board.get_ep_visibility()): 
            col = square % 8
            row = (square-col) / 8 
            image = self.piece_images[f"{'b' if self.board.turn else 'w'}p"]
            x1 = col * self.square_size
            y1 = (7 - row) * self.square_size 
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size 
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffe84a", tags="fog")
            self.canvas.create_image(x1 + self.square_size // 2, y1 + self.square_size // 2, image=image, tags="fog")
                        
        if self.board.turn: #If white turn
            print("Fog overlay has been drawn for white player.")
        else:
            print("Fog overlay has been drawn for black player.")
            
    def show_possible_moves(self, square: chess.Square):
        """Show dots on squares where the selected piece can move."""
        for move in self.board.fow_legal_moves:
            if move.from_square == square:
                # Calculate the position of the destination square
                to_col = chess.square_file(move.to_square)
                to_row = 7 - chess.square_rank(move.to_square)
                
                # Place a dot in the center of each possible move square
                x = to_col * self.square_size + self.square_size // 2
                y = to_row * self.square_size + self.square_size // 2
                self.canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5,
                    fill="blue", tags="dot"
                )
                
    def clear_dots(self):
        self.canvas.delete("dot")
                
    def draw_cover(self):
        """Draw a black cover over the board to hide it."""
        x1 = 0
        y1 = 0
        x2 = x1 + 8 * self.square_size
        y2 = y1 + 8 * self.square_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="black",tags="cover")
        
    def clear_cover(self):
        """Remove the black cover over the board to reveal it."""
        self.canvas.delete("cover")