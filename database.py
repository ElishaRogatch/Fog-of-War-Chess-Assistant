import chess
import sqlite3

class Database:
    def __init__(self, root, board, connection, cursor):
        self.root = root
        self.board = board
        self.connection = connection
        self.cursor = cursor
        # Create a button to print the moves made in the game
        self.move_list = []
        # creates the table chessboard
        self.cursor.execute("DROP TABLE IF EXISTS chessboard")
        self.cursor.execute("DROP TABLE IF EXISTS FoW_Chessboard")
        self.cursor.execute("""
        CREATE TABLE chessboard (
            col CHAR(1),
            rw INT,
            color CHAR(1),
            piece CHAR(1),
            visW BOOLEAN,
            visB BOOLEAN,
            CHECK (NOT(color = 'W' AND visW = false)),
            CHECK (NOT(color = 'B' AND visB = false))
        )
        """)
        print("Table is created")
        self.connection.commit()
        # drops captured table
        self.cursor.execute("DROP TABLE IF EXISTS captured")
        self.cursor.execute("""
        CREATE TABLE captured (
            piece CHAR(1)
        )
        """)

    def print_moves(self):
        """Print the moves made so far in the game."""
        print("Moves made in the game: ")
        for move in self.move_list:
            print(move)
    
    # refills the board at the beginning of the game
    def refill_board(self):
        # Repopulate the table with the initial chessboard setup and set visibility to TRUE
        initial_setup = [
            ('A', 1, 'W', 'R', True, True),
            ('B', 1, 'W', 'N', True, True),
            ('C', 1, 'W', 'B', True, True),
            ('D', 1, 'W', 'Q', True, True),
            ('E', 1, 'W', 'K', True, True),
            ('F', 1, 'W', 'B', True, True),
            ('G', 1, 'W', 'N', True, True),
            ('H', 1, 'W', 'R', True, True),
            ('A', 2, 'W', 'P', True, True),
            ('B', 2, 'W', 'P', True, True),
            ('C', 2, 'W', 'P', True, True),
            ('D', 2, 'W', 'P', True, True),
            ('E', 2, 'W', 'P', True, True),
            ('F', 2, 'W', 'P', True, True),
            ('G', 2, 'W', 'P', True, True),
            ('H', 2, 'W', 'P', True, True),
            ('A', 3, '', '', True, True),
            ('B', 3, '', '', True, True),
            ('C', 3, '', '', True, True),
            ('D', 3, '', '', True, True),
            ('E', 3, '', '', True, True),
            ('F', 3, '', '', True, True),
            ('G', 3, '', '', True, True),
            ('H', 3, '', '', True, True),
            ('A', 4, '', '', True, True),
            ('B', 4, '', '', True, True),
            ('C', 4, '', '', True, True),
            ('D', 4, '', '', True, True),
            ('E', 4, '', '', True, True),
            ('F', 4, '', '', True, True),
            ('G', 4, '', '', True, True),
            ('H', 4, '', '', True, True),
            ('A', 5, '', '', True, True),
            ('B', 5, '', '', True, True),
            ('C', 5, '', '', True, True),
            ('D', 5, '', '', True, True),
            ('E', 5, '', '', True, True),
            ('F', 5, '', '', True, True),
            ('G', 5, '', '', True, True),
            ('H', 5, '', '', True, True),
            ('A', 6, '', '', True, True),
            ('B', 6, '', '', True, True),
            ('C', 6, '', '', True, True),
            ('D', 6, '', '', True, True),
            ('E', 6, '', '', True, True),
            ('F', 6, '', '', True, True),
            ('G', 6, '', '', True, True),
            ('H', 6, '', '', True, True),
            ('A', 7, 'B', 'p', True, True),
            ('B', 7, 'B', 'p', True, True),
            ('C', 7, 'B', 'p', True, True),
            ('D', 7, 'B', 'p', True, True),
            ('E', 7, 'B', 'p', True, True),
            ('F', 7, 'B', 'p', True, True),
            ('G', 7, 'B', 'p', True, True),
            ('H', 7, 'B', 'p', True, True),
            ('A', 8, 'B', 'r', True, True),
            ('B', 8, 'B', 'n', True, True),
            ('C', 8, 'B', 'b', True, True),
            ('D', 8, 'B', 'q', True, True),
            ('E', 8, 'B', 'k', True, True),
            ('F', 8, 'B', 'b', True, True),
            ('G', 8, 'B', 'n', True, True),
            ('H', 8, 'B', 'r', True, True)
        ]

        query = "INSERT INTO chessboard (col, rw, color, piece, visW, visB) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.executemany(query, initial_setup)
        self.connection.commit()

        print("Board has been filled with initial chess setup.")

    def update_visibility_white(self, legal_moves):
        """Update the visibility of the squares. Loop through the table, if the square (rw, col) is not in legal_moves then visW=false."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        
        # Create a list of legal moves in the form of squares (e.g., A1, B1, etc.)
        move_list = [chess.square_name(move.to_square).upper() for move in legal_moves]
        print(f"Legal moves for white: {move_list}")
        
        # Iterate over each row in the chessboard table
        for row in results:
            # Combine the column (col) and row (rw) to create the square identifier (e.g., A1, B1)
            square = row[0] + str(row[1])  # row[0] = col, row[1] = rw
            
            # Check if the square is a legal move
            if square in move_list:
                # Update visibility to true for legal moves
                self.cursor.execute("UPDATE chessboard SET visW = true WHERE col = ? AND rw = ?", (row[0], row[1]))
            else:
                # If the square is not in the move_list, it should not be visible to the white player
                # Skip updating if the square is white and avoid violating constraints
                if row[2] != 'W':  # Only update non-white pieces (color != 'W')
                    self.cursor.execute("UPDATE chessboard SET visW = false WHERE col = ? AND rw = ?", (row[0], row[1]))

        # Commit the updates after looping through all rows
        self.connection.commit()  # Explicit commit for SQLite
        print("Visibility for white player updated.")

    def update_visibility_black(self, legal_moves):
        """Update the visibility of the squares. Loop through the table, if the square (rw, col) is not in legal_moves then visB=false."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        
        # Create a list of legal moves in the form of squares (e.g., A1, B1, etc.)
        move_list = [chess.square_name(move.to_square).upper() for move in legal_moves]
        print(f"Legal moves for black: {move_list}")
        
        # Iterate over each row in the chessboard table
        for row in results:
            # Combine the column (col) and row (rw) to create the square identifier (e.g., A1, B1)
            square = row[0] + str(row[1])  # row[0] = col, row[1] = rw
            
            # Check if the square is a legal move
            if square in move_list:
                # Update visibility to true for legal moves
                self.cursor.execute("UPDATE chessboard SET visB = true WHERE col = ? AND rw = ?", (row[0], row[1]))
            else:
                # If the square is not in the move_list, it should not be visible to the black player
                # Skip updating if the square is black and avoid violating constraints
                if row[2] != 'B':  # Only update non-black pieces (color != 'B')
                    self.cursor.execute("UPDATE chessboard SET visB = false WHERE col = ? AND rw = ?", (row[0], row[1]))

        # Commit the updates after looping through all rows
        self.connection.commit()  # Explicit commit for SQLite
        print("Visibility for black player updated.")

    def update_database(self, from_square, to_square, is_white_turn):
        """Update the MySQL database after a move."""
        from_col = chr(chess.square_file(from_square) + ord('A'))
        from_row = chess.square_rank(from_square) + 1
        to_col = chr(chess.square_file(to_square) + ord('A'))
        to_row = chess.square_rank(to_square) + 1

        # Get the piece to move
        piece = self.board.piece_at(to_square).symbol()

        # Clear the 'from' position in the database
        self.cursor.execute(
            "UPDATE chessboard SET color = '', piece = '' WHERE col = ? AND rw = ?",
            (from_col, from_row)
        )

        if is_white_turn:
            # Set the 'to' position in the database for white's turn
            self.cursor.execute(
                "UPDATE chessboard SET color = 'W', piece = ? WHERE col = ? AND rw = ?",
                (piece, to_col, to_row)
            )
        else:
            # Set the 'to' position in the database for black's turn
            self.cursor.execute(
                "UPDATE chessboard SET color = 'B', piece = ? WHERE col = ? AND rw = ?",
                (piece, to_col, to_row)
            )

        # Commit the changes
        self.connection.commit()  # Commit the changes to the SQLite database