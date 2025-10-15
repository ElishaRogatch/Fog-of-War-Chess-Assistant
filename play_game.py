import chess
import tkinter as tk
from tkinter import messagebox




class PlayGame:
    def __init__(self, root, board, canvas, square_size, board_draw, connection, cursor, database, game_over, is_white_turn, engine, bias):
        self.root = root
        # Chess board size
        self.board = board
        # Create Canvas to draw chessboard
        self.canvas = canvas
        self.square_size = square_size
        self.board_draw = board_draw
        self.connection = connection
        self.cursor = cursor
        self.database = database
        self.game_over = game_over
        self.is_white_turn = is_white_turn
        # Track dots for move indicators
        self.move_dots = []
        # Track selected square and moves
        self.selected_square = None
        self.suggest_move_button = tk.Button(self.root, text="Make Suggestion",command=self.start_engine)
        self.engine = engine
        self.turn_label = tk.Label(self.root, text="White's Turn", font=16)
        self.turn_label.pack()
        self.bias = bias

    def update_suggest_button_state(self):
        if self.is_white_turn:
            self.suggest_move_button.config(state=tk.NORMAL)
        else:
            self.suggest_move_button.config(state=tk.DISABLED)

    def start_engine(self): 
        # Run the engine
        self.engine.run_engine(self.bias) 

    # updates the button state so its enbaled or not
    def update_suggest_button_state(self):
        if self.is_white_turn:
            self.suggest_move_button.config(state=tk.NORMAL)
        else:
            self.suggest_move_button.config(state=tk.DISABLED)

    def update_turn_label(self):
        current_turn = "White's Turn" if self.is_white_turn else "Black's Turn"
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
            if piece and piece.color == self.is_white_turn:  # Ensure the player selects their own piece
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
                
                # end of og onto new way to stop castling problem
                # Check if this is a castling move:
                if self.board.is_castling(move):
                    self.handle_castling(move)
                    if self.is_white_turn:
                        self.database.move_list.append(move.uci())
                else:
                    self.capture_piece(clicked_square, self.selected_square)
                    self.board.push(move)
                    self.board_draw.update_pieces()
                    if self.is_white_turn:
                        self.database.move_list.append(move.uci())
                    self.database.update_database(self.selected_square, clicked_square, self.is_white_turn)
                
                # updates the visibility part of the database for player 1's perspective only
                # I have it set to not because where it is located it will see the next player 1's move options therefore after the piece is moved
                if not self.is_white_turn:
                    self.database.update_visibility_white(list(self.board.fow_legal_moves))
                
                if self.is_white_turn:
                    self.database.update_visibility_black(list(self.board.fow_legal_moves))

                # Check for game-ending conditions
                if self.game_over.check_game_over(self.is_white_turn):
                    return

                # Switch turns between players and functionalites
                self.is_white_turn = not self.is_white_turn
                self.update_suggest_button_state()
                self.update_turn_label()
                if self.is_white_turn:
                    self.board_draw.draw_fog_white()
                else: 
                    self.board_draw.draw_fog_black()
            else:
                messagebox.showerror("Illegal Move", "That move is not legal.")

            # Reset selected square
            self.selected_square = None

    # Extra move is handled and then set to a seperate function that updates the board
    def handle_castling(self, move):
        # Push the castling move onto the board and update the GUI.
        self.board.push(move)
        self.board_draw.update_pieces()
        
        # Determine which castling move it is and update the database accordingly.
        if self.is_white_turn:
            if move.to_square == chess.G1:  # White kingside castling: King: E1 -> G1, Rook: H1 -> F1
                self.update_database_castling('E1', 'G1', 'H1', 'F1', 'W')
            elif move.to_square == chess.C1:  # White queenside castling: King: E1 -> C1, Rook: A1 -> D1
                self.update_database_castling('E1', 'C1', 'A1', 'D1', 'W')
        else:
            if move.to_square == chess.G8:  # Black kingside castling: King: E8 -> G8, Rook: H8 -> F8
                self.update_database_castling('E8', 'G8', 'H8', 'F8', 'B')
            elif move.to_square == chess.C8:  # Black queenside castling: King: E8 -> C8, Rook: A8 -> D8
                self.update_database_castling('E8', 'C8', 'A8', 'D8', 'B')

    # updates the SQLite table to reflect the 2 move in 1 due to castling
    def update_database_castling(self, king_from, king_to, rook_from, rook_to, color):
        # Remove the king from its starting square
        self.cursor.execute(
            "UPDATE chessboard SET color = '', piece = '' WHERE col = ? AND rw = ?",
            (king_from[0], int(king_from[1]))
        )
        # Place the king on its destination square
        king_piece = 'K' if color == 'W' else 'k'
        self.cursor.execute(
            "UPDATE chessboard SET color = ?, piece = ? WHERE col = ? AND rw = ?",
            (color, king_piece, king_to[0], int(king_to[1]))
        )
        # Remove the rook from its starting square
        self.cursor.execute(
            "UPDATE chessboard SET color = '', piece = '' WHERE col = ? AND rw = ?",
            (rook_from[0], int(rook_from[1]))
        )
        # Place the rook on its destination square
        rook_piece = 'R' if color == 'W' else 'r'
        self.cursor.execute(
            "UPDATE chessboard SET color = ?, piece = ? WHERE col = ? AND rw = ?",
            (color, rook_piece, rook_to[0], int(rook_to[1]))
        )
        self.connection.commit()

    def capture_piece(self, clicked_square, selected_square):
        captured_piece = self.board.piece_at(clicked_square)
        print("I made it here! I am going to capture", captured_piece)
        if captured_piece: # if captured_piece is not None
            #if capture_piece 
            print("I actually captured", captured_piece, "here!")
            self.cursor.execute("INSERT INTO captured (piece) VALUES (?)", (captured_piece.symbol()))

        # if (self.board.piece_at(selected_square) == 'P' or self.board.piece_at(selected_square) == 'p') and (clicked_square >= 56 or clicked_square <= 7):
        #     promote()

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