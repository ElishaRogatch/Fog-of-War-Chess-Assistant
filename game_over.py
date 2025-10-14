import tkinter as tk
from tkinter import messagebox
import sqlite3

class GameOver: 
    def __init__(self, root, cursor, connection, board):
        self.root = root
        self.board = board
        self.connection = connection
        self.cursor = cursor

    def quit_game(self):
        # Resets the SQLite table
        self.cursor.execute("DROP TABLE IF EXISTS chessboard")  # Safely drops the table if it exists
        print("Table chessboard has been dropped")
        self.connection.commit()
        self.cursor.execute("DROP TABLE IF EXISTS captured")  # Safely drops the table if it exists
        print("Table captured has been dropped")
        self.connection.commit()

        # Close the SQLite connection
        self.connection.close()
        print("SQLite connection closed")

        # Close the GUI window
        self.root.quit()
        print("Game ended")

    def check_game_over(self, is_white_turn):
        captured_list = []
        self.cursor.execute("SELECT * FROM captured;")
        results = self.cursor.fetchall()
        # Print each row to the console
        for captured in results:
            print(captured[0])  # Prints each row from the database
            captured_list.append(captured[0])

        """Check if the game is over (checkmate, stalemate, etc.)."""
        if len(captured_list) > 1 and (captured_list[-1] == 'K' or captured_list[-1] == 'k'):
            winner = "Black" if not is_white_turn else "White"
            messagebox.showinfo("Checkmate", f"{winner} wins!")
            self.quit_game()
            # print(self.moves)
            return True
        elif self.board.is_stalemate():
            messagebox.showinfo("Stalemate", "It's a draw!")
            self.quit_game()
            # print(self.moves)
            return True
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Draw", "Insufficient material for checkmate!")
            self.quit_game()
            # print(self.moves)
            return True
        return False