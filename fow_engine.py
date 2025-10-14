import chess
import chess.engine
import sqlite3
import json
from output_processor import OutputProcessor
#from prediction_tree import PredictionTree
import platform
from bias_eval import BiasScorer
import tkinter as tk
from tkinter import messagebox


class FoW_Engine1:
    def __init__(self, connection):
        self.connection = sqlite3.connect("fogofwar.db")
        self.cursor = self.connection.cursor()
        self.prediction_tree = None


    def run_engine(self, bias_dict):
        system_name = platform.system()
        if system_name == "Windows":
            SF_Path = "stockfish-windows-x86-64-sse41-popcnt.exe"
        elif system_name == "Darwin":  #MacOS
            SF_Path = "our path to stockfish MACOS"
        elif system_name == "Linux":
            SF_Path = "our path to stockfish Linux"
        print(f"[DEBUG] Using Stockfish at: {SF_Path}")

        self.engine = chess.engine.SimpleEngine.popen_uci(SF_Path)
        self.board = chess.Board()
        self.board.clear()
        self.bias = bias_dict
        self.bias_scorer = BiasScorer(self.bias)
        print(f"[DEBUG] Bias config loaded: {self.bias}")
        # self.prediction_tree = PredictionTree(self.board, initial_turn=0)  # Temporarily disabled for trial

        print("[DEBUG] Initializing visible pieces from database...")
        self.initialize_visible_pieces()
        print("visible pieces initialized")
        print("Evaluating predictions")
        self.evaluate_moves()
        print("board after prediction")
        print(self.board)
        print("Suggesting best move options")
        self.suggest_player_move()

    def initialize_visible_pieces(self):
        """Initialize the visible pieces from the database."""
        initial_setup = [
            ('A', 1, '', '', False, 1.0),
            ('B', 1, '', '', False, 1.0),
            ('C', 1, '', '', False, 1.0),
            ('D', 1, '', '', False, 1.0),
            ('E', 1, '', '', False, 1.0),
            ('F', 1, '', '', False, 1.0),
            ('G', 1, '', '', False, 1.0),
            ('H', 1, '', '', False, 1.0),
            ('A', 2, '', '', False, 1.0),
            ('B', 2, '', '', False, 1.0),
            ('C', 2, '', '', False, 1.0),
            ('D', 2, '', '', False, 1.0),
            ('E', 2, '', '', False, 1.0),
            ('F', 2, '', '', False, 1.0),
            ('G', 2, '', '', False, 1.0),
            ('H', 2, '', '', False, 1.0),
            ('A', 3, '', '', False, 1.0),
            ('B', 3, '', '', False, 1.0),
            ('C', 3, '', '', False, 1.0),
            ('D', 3, '', '', False, 1.0),
            ('E', 3, '', '', False, 1.0),
            ('F', 3, '', '', False, 1.0),
            ('G', 3, '', '', False, 1.0),
            ('H', 3, '', '', False, 1.0),
            ('A', 4, '', '', False, 1.0),
            ('B', 4, '', '', False, 1.0),
            ('C', 4, '', '', False, 1.0),
            ('D', 4, '', '', False, 1.0),
            ('E', 4, '', '', False, 1.0),
            ('F', 4, '', '', False, 1.0),
            ('G', 4, '', '', False, 1.0),
            ('H', 4, '', '', False, 1.0),
            ('A', 5, '', '', False, 1.0),
            ('B', 5, '', '', False, 1.0),
            ('C', 5, '', '', False, 1.0),
            ('D', 5, '', '', False, 1.0),
            ('E', 5, '', '', False, 1.0),
            ('F', 5, '', '', False, 1.0),
            ('G', 5, '', '', False, 1.0),
            ('H', 5, '', '', False, 1.0),
            ('A', 6, '', '', False, 1.0),
            ('B', 6, '', '', False, 1.0),
            ('C', 6, '', '', False, 1.0),
            ('D', 6, '', '', False, 1.0),
            ('E', 6, '', '', False, 1.0),
            ('F', 6, '', '', False, 1.0),
            ('G', 6, '', '', False, 1.0),
            ('H', 6, '', '', False, 1.0),
            ('A', 7, 'B', 'p', False, 1.0),
            ('B', 7, 'B', 'p', False, 1.0),
            ('C', 7, 'B', 'p', False, 1.0),
            ('D', 7, 'B', 'p', False, 1.0),
            ('E', 7, 'B', 'p', False, 1.0),
            ('F', 7, 'B', 'p', False, 1.0),
            ('G', 7, 'B', 'p', False, 1.0),
            ('H', 7, 'B', 'p', False, 1.0),
            ('A', 8, 'B', 'r', False, 1.0),
            ('B', 8, 'B', 'n', False, 1.0),
            ('C', 8, 'B', 'b', False, 1.0),
            ('D', 8, 'B', 'q', False, 1.0),
            ('E', 8, 'B', 'k', False, 1.0),
            ('F', 8, 'B', 'b', False, 1.0),
            ('G', 8, 'B', 'n', False, 1.0),
            ('H', 8, 'B', 'r', False, 1.0)
        ]

        # Check if the table exists
        self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM sqlite_master
                    WHERE type = 'table' AND name = 'FoW_chessboard';
                """)

        table_exists = self.cursor.fetchone()[0] > 0

        # If the table doesn't exist, create it and insert the initial setup
        if not table_exists:
            # Create table with unique constraint during creation
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS FoW_chessboard (
                            col CHAR(1),
                            rw INTEGER,
                            color CHAR(1),
                            piece CHAR(1),
                            visW INTEGER,  -- BOOLEAN substitute; use 0 and 1 for False and True
                            prob FLOAT,
                            UNIQUE(col, rw)  -- Unique constraint added here
                        );
                    """)
            self.connection.commit()

            # Insert the initial setup data into the table
            query = "INSERT INTO FoW_chessboard (col, rw, color, piece, visW, prob) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.executemany(query, initial_setup)
            self.connection.commit()

            # Additional logic to repopulate visible pieces (if needed)

            self.cursor.execute("""
                        INSERT OR REPLACE INTO FoW_chessboard (col, rw, color, piece, visW, prob)
                        SELECT col, rw, color, piece, visW, 1.0
                        FROM chessboard
                        WHERE visW = 1;
                    """)
            self.connection.commit()

        else:
            # If the table exists, just update the visible pieces
            self.cursor.execute("""
                        INSERT OR REPLACE INTO FoW_chessboard (col, rw, color, piece, visW, prob)
                        SELECT col, rw, color, piece, visW, 1.0
                        FROM chessboard
                        WHERE visW = 1;
                    """)
            self.cursor.execute(
                """DELETE FROM FoW_chessboard WHERE rw = 7 AND piece = 'p' AND col IN ( SELECT col FROM FoW_chessboard WHERE rw < 7 AND piece = 'p' );""")
            self.connection.commit()

    def evaluate_moves(self):
        self.cursor.execute("SELECT col, rw, color, piece, visW, prob FROM FoW_chessboard;")
        FoW_chessboard = self.cursor.fetchall()

        # Populate the board with visible pieces
        for col, rw, color, piece, vis, prob in FoW_chessboard:
            square = chess.square(ord(col) - ord('A'), rw - 1)
            if piece == '':
                self.board.remove_piece_at(square)

            if color == 'W':
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.upper()))
            elif color == 'B':
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.lower()))
            else:
                continue
        print("board with visible pieces")
        print(self.board)
        self.board.turn = chess.BLACK

        # Get top moves from Stockfish for black
        try:
            analysis = self.engine.analyse(self.board, chess.engine.Limit(depth=1), multipv=5)
            if not isinstance(analysis, list):
                analysis = [analysis]

            # Score and sort moves
            scored_guesses = []
            for entry in analysis:
                move = entry["pv"][0]
                if self.move_enters_visible_area(move):
                    continue  # Skip moves that land on visible squares,


                stockfish_score = entry["score"].pov(self.board.turn).score(mate_score=10000)
                adjusted_score = self.bias_scorer.get_bias_score(move, stockfish_score, self.board, is_black_turn=True)
                scored_guesses.append((move, adjusted_score))

            # Sort moves by score
            scored_guesses.sort(key=lambda x: x[1], reverse=True)

            # Take the best move
            best_move, best_score = scored_guesses[0]

            # Push the best move to the board
            self.board.push(best_move)

            # Store the move in the database
            to_col = chr(chess.square_file(best_move.to_square) + ord('A'))
            to_rw = chess.square_rank(best_move.to_square) + 1
            moving_piece = self.board.piece_at(best_move.to_square)

            self.cursor.execute("""
                    INSERT OR REPLACE INTO FoW_chessboard (col, rw, color, piece, visW, prob)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (to_col, to_rw, 'B', moving_piece.symbol().lower(), 0, 0.5))

            self.connection.commit()

        except Exception as e:
            print(f"Stockfish error: {e}")

    def suggest_player_move(self, max_guesses=5):
        try:
            if not hasattr(self, 'engine') or self.engine is None:
                self.engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-sse41-popcnt.exe")

            self.board.turn = chess.WHITE

            analysis = self.engine.analyse(self.board, chess.engine.Limit(depth=1), multipv=max_guesses)
            if not isinstance(analysis, list):
                analysis = [analysis]

            scored_guesses = []
            for entry in analysis:
                move = entry["pv"][0]
                stockfish_score = entry["score"].pov(self.board.turn).score(mate_score=10000)
                if stockfish_score is None:
                    stockfish_score = 0
                adjusted_score = self.bias_scorer.get_bias_score(move, stockfish_score, self.board, is_black_turn=False)
                scored_guesses.append((move, adjusted_score))

            scored_guesses.sort(key=lambda x: x[1], reverse=True)
            print("Suggested Moves for White:")
            for i, (move, score) in enumerate(scored_guesses[:max_guesses]):
                print(f"{i + 1}. Move: {move}, Score: {score}")

            messagebox.showinfo("Top 5 Move Suggestions and Scores", scored_guesses)


        finally:
            try:
                if self.engine:
                    self.engine.quit()
            except chess.engine.EngineTerminatedError:
                print("Engine already terminated.")

    def move_enters_visible_area(self, move):
        # Check if the destination square of the move is currently visible to the player
        col = chr(chess.square_file(move.to_square) + ord('A'))
        rw = chess.square_rank(move.to_square) + 1

        self.cursor.execute("""
            SELECT visW FROM FoW_chessboard
            WHERE col = ? AND rw = ?
        """, (col, rw))
        result = self.cursor.fetchone()

        if result and result[0] == 1:
            return True
        return False


