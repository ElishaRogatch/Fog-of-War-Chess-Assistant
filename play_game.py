import chess
import tkinter as tk
from board_state_limiter import BoardStateLimiter
from probable_state_analyzer import ProbableStateAnalyzer
import copy

class PlayGame:
    def __init__(self, root, board, canvas, square_size, assisted_player, board_draw, game_over, engine, bias):
        """Initialize game state and GUI elements."""
        self.root = root

        # Chess board size
        self.board = board

        # Create Canvas to draw chessboard
        self.canvas = canvas
        self.square_size = square_size
        self.assisted_player = assisted_player
        self.board_draw = board_draw
        self.game_over = game_over

        # Track selected square and moves
        self.selected_square = None
        self.suggest_move_button = tk.Button(self.root, text="Make Suggestion",command= lambda: self.engine.suggest_player_move(self.BSL, self.PSA))
        self.transition_sides_button = tk.Button(self.root, text="Player Transition Toggle", command= lambda: self.update_transition_sides_state())
        self.engine = engine
        self.BSL = BoardStateLimiter(self.board, [copy.deepcopy(self.board)])
        self.PSA = ProbableStateAnalyzer(self.BSL, self.engine, bias)
        self.turn_label = tk.Label(self.root, text="White's Turn", font=16)
        self.turn_label.pack()
        self.bias = bias
        self.captured_pieces = []
        self.transition_sides = tk.BooleanVar(root, value=False)
        self.wait_lock = tk.BooleanVar(root, value=False)

    def update_suggest_button_state(self):
        """Updates the button state so its enbaled or not based on whose turn it is."""
        if self.assisted_player == self.board.turn:
            self.suggest_move_button.config(state=tk.NORMAL)
        else:
            self.suggest_move_button.config(state=tk.DISABLED)
    
    def update_transition_sides_state(self):
        """Updates the transition sides button state and variable."""
        if self.transition_sides.get():
            self.transition_sides_button.config(bg="SystemButtonShadow")
            self.transition_sides.set(False)
        else:
            self.transition_sides_button.config(bg="SystemButtonFace")
            self.transition_sides.set(True)

    def update_turn_label(self):
        """Updates the turn label to show whose turn it is."""
        current_turn = "White's Turn" if self.board.turn else "Black's Turn"
        self.turn_label.config(text=current_turn)
        
    def on_square_click(self, event):
        """Handle click events to select and move pieces."""
        col = 7-(event.x // self.square_size)
        row = 7-(event.y // self.square_size)
        col = 7 - col # reverse the column mapping
        clicked_square = chess.square(col, row) # placed here so that it is storing the current player's moves and not the next player

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
            # Try to make a move with promotion if applicable
            if (str(self.board.piece_at(self.selected_square)).upper()=='P' and (clicked_square >= 56 or clicked_square <= 7)):
                move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"q")
                ask_promotion = True
            else:
                # Make normal move without promotion
                move = chess.Move(self.selected_square, clicked_square)
                ask_promotion = False
            if move in self.board.fow_legal_moves:
                if ask_promotion:
                    # Have user choose promotion piece
                    promotion_piece = tk.StringVar(value="Queen")
                    self.root.wait_window(self.display_promotion_box(promotion_piece)) # pause code execution until user makes a choice
                    if promotion_piece.get() == "Knight":
                        move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"n")
                    elif promotion_piece.get() == "Bishop":
                        move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"b")
                    elif promotion_piece.get() == "Rook":
                        move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"r")
                    else: # Selected piece is queen
                        move = chess.Move.from_uci(str(chess.Move(self.selected_square, clicked_square))+"q")
                captured_piece = self.board.piece_at(clicked_square)
                if captured_piece: # if captured_piece is not None
                    print(f"{chess.COLOR_NAMES[captured_piece.color]} {chess.PIECE_NAMES[captured_piece.piece_type]} was captured!")
                    self.captured_pieces.append(captured_piece.symbol())
                # Update the board with the move
                self.board.push(move)
                # Check for game-ending conditions
                if self.game_over.check_game_over():
                    return
                # Show board after move for player (do early in case BSL and PSA take some time to compute ??)
                if self.transition_sides.get():
                    self.board.push(chess.Move.null())
                    self.board_draw.update_pieces()
                    self.board_draw.draw_fog()
                    self.canvas.update_idletasks()
                    self.board.pop()
                # Switch turns between players and functionalites
                self.update_suggest_button_state()
                if self.assisted_player == self.board.turn: # Non-assisted player just moved
                    self.BSL.pre_move_limiting()
                    print(f"Number of potential pre-turn states {len(self.BSL.board_states)}")
                    self.PSA.analyze_states()
                    print(f"Board scores \n{self.PSA.board_scores}")
                else: # Assisted player just moved
                    self.BSL.post_move_limiting()
                    print(f"Number of potential post-turn states {len(self.BSL.board_states)}")
                
                if self.transition_sides.get():
                    # Wait for next player, Black out board, Draw the board and fog for the next player
                    self.canvas.unbind("<Button-1>")
                    self.root.wait_variable(self.wait_lock)
                    self.wait_lock.set(False)
                    self.canvas.bind("<Button-1>", self.on_square_click)
                    self.board_draw.update_pieces()
                    self.board_draw.draw_fog()
                    self.board_draw.draw_cover()
                    self.canvas.unbind("<Button-1>")
                    self.root.wait_variable(self.wait_lock)
                    self.canvas.delete("cover")
                    self.wait_lock.set(False)
                    self.canvas.bind("<Button-1>", self.on_square_click)
                    self.update_turn_label()
                else:
                    # Draw the board and fog for the next player
                    self.board_draw.update_pieces()
                    self.board_draw.draw_fog()
                    self.update_turn_label()

            # Reset selected square
            self.selected_square = None      
            
    def display_promotion_box(self, promotion_piece):
        """Prompt user to select a piece for pawn promotion with the given GUI."""
        self.canvas.configure(state=tk.DISABLED)
        promotion_selection = tk.Toplevel(self.root)
        promotion_selection.geometry("300x200")
        promotion_selection.title("Pawn Promotion")
        promotion_selection.grab_set() # prevent user from interacting with other tkinter elements
        tk.Label(promotion_selection, text="Select Promotion Piece").pack(side= tk.TOP)
        tk.OptionMenu(promotion_selection, promotion_piece, "Queen", "Rook", "Bishop", "Knight").pack(side= tk.TOP)
        tk.Button(promotion_selection, text="Ok", command= lambda: promotion_selection.destroy()).pack(pady=10, side= tk.BOTTOM) 
        return promotion_selection