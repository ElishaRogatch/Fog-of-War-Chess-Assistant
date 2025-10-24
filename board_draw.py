import chess
from chess import SQUARES, Bitboard, BB_SQUARES
import fow_chess
import tkinter as tk

class DrawBoard:
    def __init__(self, root, board, board_size, square_size, canvas):
        self.root = root
        # Chess board size
        self.board_size = board_size
        self.square_size = square_size
        self.board = board
        # Create Canvas to draw chessboard
        self.canvas = canvas
        # Load piece images
        self.piece_images = self.load_piece_images()

    def load_piece_images(self):
        """Load piece images from files (you can use any chess piece images here)."""
        pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
        piece_images = {}
        for piece in pieces:
            piece_images[piece] = tk.PhotoImage(file=f"images/{piece}.png")
        return piece_images
    
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
        self.canvas.delete("piece")
        # Place pieces on the board
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_str = piece.symbol().lower() if piece.color else piece.symbol()
                    image = self.piece_images.get(f"{'w' if piece.color else 'b'}{piece_str.lower()}")
                    if image:
                        x = col * self.square_size
                        y = row * self.square_size
                        self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, 
                                                 image=image, tags="piece")
        
    def draw_fog(self):
        """Draws a fog overlay on squares that aren't visible to the white player."""
        # Clear any previous fog overlay
        self.canvas.delete("fog")
        
        # Define the fog color (you can use a semi-transparent color or adjust opacity)
        if self.board.turn: #If white turn
            fog_color = "red"  # Light red with transparency (note: Tkinter doesn't support RGBA natively, so use a solid color or check transparency options for your canvas)
        else:
            fog_color = "purple"  # You can adjust the color as needed
        
        BB_VISIBILITY: Bitboard = self.board.get_fow_visibility()
        for square in SQUARES:
            if not BB_SQUARES[square] & BB_VISIBILITY: #If the square is not visible
                col = square % 8
                row = (square - col) / 8
                # Calculate the pixel coordinates for the square; 8x8 board with A1 at bottom-left
                x1 = col * self.square_size
                y1 = (7 - row) * self.square_size  
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Draw a fog rectangle over the square
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fog_color, tags="fog")
        
        if self.board.turn: #If white turn
            print("Fog overlay has been drawn for white player.")
        else:
            print("Fog overlay has been drawn for black player.")