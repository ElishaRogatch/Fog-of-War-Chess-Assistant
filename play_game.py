import chess
import tkinter as tk
from board_state_limiter import BoardStateLimiter
import copy

class PlayGame:
    def __init__(self, root, board, canvas, square_size, board_draw, game_over, engine, bias):
        self.root = root
        # Chess board size
        self.board = board
        # Create Canvas to draw chessboard
        self.canvas = canvas
        self.square_size = square_size
        self.board_draw = board_draw
        self.game_over = game_over
        # Track dots for move indicators
        # Track selected square and moves
        self.selected_square = None
        self.suggest_move_button = tk.Button(self.root, text="Make Suggestion",command=self.start_engine)
        self.engine = engine
        self.turn_label = tk.Label(self.root, text="White's Turn", font=16)
        self.turn_label.pack()
        self.bias = bias
        self.captured_pieces = []
        self.BSL = BoardStateLimiter(self.board, [copy.deepcopy(self.board)])

    def start_engine(self): 
        # Run the engine
        self.engine.run_engine(self.bias) 

    # updates the button state so its enbaled or not
    def update_suggest_button_state(self):
        if self.board.turn:
            self.suggest_move_button.config(state=tk.NORMAL)
        else:
            self.suggest_move_button.config(state=tk.DISABLED)

    def update_turn_label(self):
        current_turn = "White's Turn" if self.board.turn else "Black's Turn"
        self.turn_label.config(text=current_turn)
        
    def on_square_click(self, event):
        """Handle click events to select and move pieces."""
        col = 7-(event.x // self.square_size)
        row = 7-(event.y // self.square_size)
        col = 7 - col # reverse the column mapping
        clicked_square = chess.square(col, row)
        # placed here so that it is storing the current player's moves and not the next player

        # Clear existing move dots when clicking a new square
        for dot in self.board_draw.move_dots:
            self.canvas.delete(dot)
        self.board_draw.move_dots = []

        if self.selected_square is None:
            # Select the piece if any
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.board.turn:  # Ensure the player selects their own piece
                self.selected_square = clicked_square
                # Display possible moves for the selected piece
                self.board_draw.show_possible_moves(clicked_square)
        else:
            # Try to make a move
            if (str(self.board.piece_at(self.selected_square)).upper()=='P' and (clicked_square >= 56 or clicked_square <= 7)):
                # have user choose promotion piece
                self.canvas.configure(state=tk.DISABLED)
                promotion_selection = tk.Toplevel(self.root)
                promotion_selection.geometry("300x200")
                promotion_selection.title("Pawn Promotion")
                promotion_selection.grab_set() # prevent user from interacting with other tkinter elements
                promotion_piece = tk.StringVar(value="Queen")
                tk.Label(promotion_selection, text="Select Promotion Piece").pack(side= tk.TOP)
                tk.OptionMenu(promotion_selection, promotion_piece, "Queen", "Rook", "Bishop", "Knight").pack(side= tk.TOP)
                tk.Button(promotion_selection, text="Ok", command= lambda: promotion_selection.destroy()).pack(pady=10, side= tk.BOTTOM)
                self.root.wait_window(promotion_selection) # pause code execution until user makes a choice
                if promotion_piece.get() == "Knight":
                    move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"n")
                elif promotion_piece.get() == "Bishop":
                    move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"b")
                elif promotion_piece.get() == "Rook":
                    move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"r")
                else: # selected piece is queen
                    move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"q")
            else:
                move = chess.Move(self.selected_square, clicked_square)
            if move in self.board.fow_legal_moves:
                captured_piece = self.board.piece_at(clicked_square)
                if captured_piece: # if captured_piece is not None
                    print(f"{chess.COLOR_NAMES[captured_piece.color]} {chess.PIECE_NAMES[captured_piece.piece_type]} was captured!")
                    self.captured_pieces.append(captured_piece.symbol())
                # make the move
                self.board.push(move)
                self.board_draw.update_pieces()
                # Check for game-ending conditions
                if self.game_over.check_game_over():
                    return
                
                # Switch turns between players and functionalites
                self.update_suggest_button_state()
                self.update_turn_label()
                # draw the fog for the player
                self.board_draw.draw_fog()
                if self.board.turn: #black just moved # BSL CODE
                    self.BSL.pre_move_limiting()
                    print(f"Number of potential pre-turn states {len(self.BSL.old_board_states)}")
                else: #white just moved
                    self.BSL.post_move_limiting()
                    print(f"Number of potential post-turn states {len(self.BSL.old_board_states)}")

            # Reset selected square
            self.selected_square = None