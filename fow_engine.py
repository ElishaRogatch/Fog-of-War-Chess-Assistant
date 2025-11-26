import chess
import chess.engine
import platform
from bias_eval import BiasScorer
import tkinter as tk

class FoW_Engine1:
    def __init__(self, board, bias):
        self.board = board
        self.bias_scorer = BiasScorer(bias)

    def start_engine(self):
        """Run the FOW engine to generate a move"""
        system_name = platform.system()
        if system_name == "Windows":
            SF_Path = "fairy-stockfish_x86-64-bmi2.exe"
        elif system_name == "Darwin":  #MacOS
            SF_Path = "our path to stockfish MACOS"
        elif system_name == "Linux":
            SF_Path = "our path to stockfish Linux"
        print(f"[DEBUG] Using Fairy Stockfish at: {SF_Path}")
        self.engine = chess.engine.SimpleEngine.popen_uci([SF_Path, "load", "variants.ini"])
        self.engine.configure({"Threads": 12})# look into this
        
    def close_engine(self):
        try:
            if self.engine:
                self.engine.quit()
        except chess.engine.EngineTerminatedError:
            print("Engine already terminated.")

    def suggest_player_move(self, BSL, PSA, max_guesses=5):
        print("Suggesting best move options")
        try:
            if not hasattr(self, 'engine') or self.engine is None:
                self.start_engine()
            
            #self.engine.protocol._ucinewgame() #use to clear engine hash tables and get consistent move output
            analyses = []
            for i in PSA.board_scores[:5]:
                if len(PSA.board_scores) >= 4:
                    search_depth = 10
                elif len(PSA.board_scores) >= 2:
                    search_depth = 12
                else: #length is 1
                    search_depth = 15
                analysis = self.engine.analyse(BSL.board_states[i[0]], chess.engine.Limit(depth=search_depth), multipv=max_guesses)
                analyses.append(analysis)
            
            scored_guesses = []
            for i, analysis in enumerate(analyses):
                board = BSL.board_states[PSA.board_scores[i][0]]
                print(board) # to help understand suggestions while testing
                vision_before_score = self.bias_scorer.get_before_vision_score(board)  #gets the vision state before to be used in determining the vision change
                for entry in analysis:
                    move = entry["pv"][0]
                    stockfish_score = entry["score"].pov(board.turn).score(mate_score=10000)
                    adjusted_score = self.bias_scorer.move_bias_applicator(move, stockfish_score, board, vision_before_score)
                    print(f"Move: {move}, Stockfish score: {stockfish_score} :: Adjusted Score: {adjusted_score}")
                    scored_guesses.append((move, adjusted_score))
                    #scored_guesses.append((move, stockfish_score))
            
            # remove duplicate moves from scored guesses
            duplicate_indicies = []
            combined_scored_guesses = []
            for i in range(len(scored_guesses)):
                if i in duplicate_indicies: continue
                total_score = scored_guesses[i][1]
                total_moves = 1
                unique_move = scored_guesses[i][0]
                for j in range(len(scored_guesses)):
                    list_move = scored_guesses[j][0]
                    if unique_move.from_square == list_move.from_square and unique_move.to_square == list_move.to_square:
                        duplicate_indicies.append(j)
                        total_score += scored_guesses[j][1]
                        total_moves += 1
                combined_scored_guesses.append((unique_move, round(total_score/ total_moves)))
            
            scored_guesses = combined_scored_guesses
            scored_guesses.sort(key=lambda x: x[1], reverse=True)
            print("Suggested Moves for White:")
            for i, (move, score) in enumerate(scored_guesses[:max_guesses]):
                print(f"{i + 1}. Move: {move}, Score: {score}")
            self.display_suggestion_box(scored_guesses)

            
        finally:
            pass
            #try:
            #    if self.engine:
            #        self.engine.quit()
            #except chess.engine.EngineTerminatedError:
            #    print("Engine already terminated.")
            
    def board_state_analysis(self, board):
        try:
            if not hasattr(self, 'engine') or self.engine is None:
                self.start_engine()

            analysis = self.engine.analyse(board, chess.engine.Limit(depth=5))
            
            stockfish_score = analysis["score"].pov(not board.turn).score(mate_score=10000)
            return stockfish_score
        
        finally:
            pass
        
    def display_suggestion_box(self, scored_guesses):
        suggestion_box = tk.Toplevel()
        suggestion_box.title("Top 5 Move Suggestions and Scores")
        suggestion_box.geometry("400x150")
        suggestion_box.grab_set()
        suggestion_box.iconbitmap("images/icons/Suggester.ico")
        tk.Label(suggestion_box, text=scored_guesses[:5], wraplength=380).pack(pady=(10, 0))
        tk.Button(suggestion_box, text="OK", command=suggestion_box.destroy).pack(pady=10,side= tk.BOTTOM)