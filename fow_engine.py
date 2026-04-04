from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chess.engine import InfoDict
    from fow_chess import FowBoard
    from game_over import GameOver
    from fow_logger import FowLogger
    from board_state_limiter import BoardStateLimiter
    from probable_state_analyzer import ProbableStateAnalyzer

import chess
import chess.engine
import platform
from bias_eval import BiasScorer
import tkinter as tk
from tkinter import filedialog
import os
from pathlib import Path
from utils import score_round
MoveScore = tuple[chess.Move, int]

class FowEngine:
    def __init__(self, root, board: FowBoard, biases: dict[str, float], game_over: GameOver, logger: FowLogger):
        self.root = root
        self.board = board
        self.bias_scorer = BiasScorer(biases)
        self.game_over = game_over
        self.logger = logger

    def start_engine(self):
        """Run the FOW engine to generate a move"""
        system_name = platform.system()
        SF_Path = Path("not_fairy_stockfish.exe")
        if system_name == "Windows":
            search_location = Path('.')
            for search_path in search_location.iterdir():
                if search_path.is_file():
                    if search_path.name[:15] == "fairy-stockfish" and search_path.name[-4:] == ".exe":
                        SF_Path = search_path
            #SF_Path = "fairy-stockfish_x86-64-bmi2.exe"
        elif system_name == "Darwin":  #MacOS
            SF_Path = Path("our path to stockfish MACOS")
        elif system_name == "Linux":
            SF_Path = Path("our path to stockfish Linux")
        try:   
            self.engine = chess.engine.SimpleEngine.popen_uci([SF_Path, "load", "variants.ini"])
        except:
            print(f"Fairy stockfish engine at \"{SF_Path}\" failed to properly open")
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            SF_Path = filedialog.askopenfilename(title= "Choose Fairy-Stockfish engine file", initialdir= cur_dir, filetypes= [("Executable", "*.exe")])
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci([SF_Path, "load", "variants.ini"])
            except:
                self.engine = None
                print(f"Fairy stockfish engine at \"{SF_Path}\" failed to properly open")
                self.logger.log("No suitable fairy stockfish engine was found.")
                self.game_over.quit_game()
                
        #self.engine.configure({"Threads": 12})# TODO look into this
        
    def close_engine(self):
        """Terminate the FOW chess engine process."""
        try:
            if self.engine:
                self.engine.quit()
        except chess.engine.EngineTerminatedError:
            print("Engine already terminated.")

    def suggest_player_move(self, BSL: BoardStateLimiter, PSA: ProbableStateAnalyzer, max_guesses=5):
        """Analyze the current board state and suggest the best moves for the assisted player."""
        self.logger.log("Best moves from PSA boards")
    
        #self.engine.protocol._ucinewgame() # Use to clear engine hash tables and get consistent move output
        analyses: list[list[InfoDict]] = []
        for i in PSA.board_scores[:5]:
            if len(PSA.board_scores) >= 4:
                search_depth = 10
            elif len(PSA.board_scores) >= 2:
                search_depth = 12
            else: # Length is 1
                search_depth = 15
            analysis = self.engine.analyse(BSL.board_states[i[0]], chess.engine.Limit(depth=search_depth), multipv=max_guesses)
            analyses.append(analysis)
        
        board_guesses: list[list[MoveScore]] = [[] for _ in range(min(len(PSA.board_scores), 5))]
        below_scores = [0] * len(board_guesses)
        for i, analysis in enumerate(analyses):
            board = BSL.board_states[PSA.board_scores[i][0]]
            self.logger.log(board) # To help understand suggestions while testing DEBUG??? or not?
            vision_before_score = self.bias_scorer.get_before_vision_score(board)  # Gets the vision state before to be used in determining the vision change
            for entry in analysis:
                move = entry["pv"][0]
                stockfish_score = entry["score"].pov(board.turn).score(mate_score=10000)
                adjusted_score = self.bias_scorer.move_bias_applicator(move, stockfish_score, board, vision_before_score)
                self.logger.log(f"Move: {move}, Stockfish score: {stockfish_score} :: Adjusted Score: {adjusted_score}")
                board_guesses[i].append((move, adjusted_score))
                
        # Iterpolate what the nth score would be using least squares regression # Improve interpolation scheme?
        if len(board_guesses[0]) >= max_guesses:
            for i in range(len(below_scores)):
                a,b = self.score_regression([move_score[1] for move_score in  board_guesses[i]])
                below_scores[i] = score_round(a + b * (max_guesses + 1))
                
        scored_guesses: list[MoveScore] = []
        duplicates = [[False for move_guess in single_board_guesses] for single_board_guesses in board_guesses]
        # Remove duplicate moves from scored guesses
        for i in range(len(board_guesses)): # For each probable board's suggestions
            for j in range(len(board_guesses[i])): # For a suggested move for one of the probable boards
                if duplicates[i][j] : continue
                total_score = board_guesses[i][j][1]
                unique_move = board_guesses[i][j][0]
                for k in range(len(board_guesses)): # Go through the other boards and look for a matching move in each board
                    if k == i: continue # Do not check the current board
                    match_found = False
                    for h in range(len(board_guesses[k])): # For each suggested move in another board
                        if duplicates[k][h] : continue
                        current_move = board_guesses[k][h][0]
                        if unique_move == current_move:
                            duplicates[k][h] = True
                            total_score += board_guesses[k][h][1]
                            match_found = True
                            break
                    if not match_found: # If a matching move is not found for a board use the guessed next score as a guess for the move's score
                        total_score += below_scores[k]
                scored_guesses.append((unique_move, score_round(total_score / len(board_guesses[0]))))
                duplicates[i][j] = True
        
        # Sort and display the top moves
        scored_guesses.sort(key=lambda x: x[1], reverse=True)
        self.logger.log("Suggested Moves for White:")
        for i, (move, score) in enumerate(scored_guesses[:max_guesses]):
            self.logger.log(f"{i + 1}. Move: {move}, Score: {score}")
        SuggestionOutput(self.root, scored_guesses)
            
    def board_state_analysis(self, board: FowBoard) -> int:
        """Analyze the board state and return Stockfish score."""
        analysis = self.engine.analyse(board, chess.engine.Limit(depth=5))
        stockfish_score  = analysis["score"].pov(not board.turn).score(mate_score=10000)
        return stockfish_score
        
    def score_regression(self, scores: list[int]) -> tuple[float, float]:
        """Perform linear regresion on the scores to form an interpolating function"""
        avg_index = len(scores) * (len(scores) + 1) / (2 * len(scores))
        score_avg = sum(scores) / len(scores)
        
        b_num = 0
        b_dem = 0
        for i in range(1, len(scores)+1):
            b_num += (i-avg_index) * (scores[i-1]-score_avg)
            b_dem += (i-avg_index) ** 2
        
        b = b_num / b_dem
        a = score_avg - b*avg_index
        return a,b
        

        
class SuggestionOutput(tk.Toplevel):
    """Display a popup with the top move suggestions and their scores."""
    def __init__(self, parent, scored_guesses: list[MoveScore]):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Suggester.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(0, 100)
        self.title("Top 5 Move Suggestions and Scores")
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=scored_guesses[:5], wraplength=380).pack(padx=10, pady=5)

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM,padx=10, pady=5)


    def ok(self):
        self.close()
       
    def close(self):
        self.destroy()