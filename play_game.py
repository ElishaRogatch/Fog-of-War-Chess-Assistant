import chess
import tkinter as tk

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
        self.move_dots = []
        # Track selected square and moves
        self.selected_square = None
        self.suggest_move_button = tk.Button(self.root, text="Make Suggestion",command=self.start_engine)
        self.engine = engine
        self.turn_label = tk.Label(self.root, text="White's Turn", font=16)
        self.turn_label.pack()
        self.bias = bias
        self.captured_pieces = []

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
        for dot in self.move_dots:
            self.canvas.delete(dot)
        self.move_dots = []

        if self.selected_square is None:
            # Select the piece if any
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.board.turn:  # Ensure the player selects their own piece
                self.selected_square = clicked_square
                # Display possible moves for the selected piece
                self.show_possible_moves(clicked_square)
        else:
            # Try to make a move
            if (str(self.board.piece_at(self.selected_square)).upper()=='P' and (clicked_square >= 56 or clicked_square <= 7)):
                # new_piece= promote() add piece choice
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
                self.board_draw.draw_fog(list(self.board.fow_legal_moves))

            # Reset selected square
            self.selected_square = None

    def show_possible_moves(self, square):
        """Show dots on squares where the selected piece can move."""
        for move in self.board.fow_legal_moves:
            if move.from_square == square:
                # Calculate the position of the destination square
                to_col = chess.square_file(move.to_square)
                to_row = 7 - chess.square_rank(move.to_square)
                
                # Place a dot in the center of each possible move square
                x = to_col * self.square_size + self.square_size // 2
                y = to_row * self.square_size + self.square_size // 2
                dot = self.canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5,
                    fill="blue", tags="dot" # the dots are blue and will stay blue lol
                )
                self.move_dots.append(dot)