import chess
import chess.engine
import platform
from bias_eval import BiasScorer
from tkinter import messagebox

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
            
            #for the best 5 boards from PSA evaluate them
            # we need to use MBA on those
            # for any duplicate moves keep only one with the mean score (compare using from_square and to_square)
            # we need to find the top 5 overall based on score (maybe top 10? potential issue with move list length) 
            # maybe give them the whole list? 
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
                for entry in analysis:
                    board = BSL.board_states[PSA.board_scores[i][0]]
                    move = entry["pv"][0]
                    stockfish_score = entry["score"].pov(board.turn).score(mate_score=10000)
                    adjusted_score = self.bias_scorer.move_bias_applicator(move, stockfish_score, board)
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
            messagebox.showinfo("Top 5 Move Suggestions and Scores", scored_guesses)
            
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
            
            stockfish_score = analysis[0]["score"].pov(board.turn).score(mate_score=10000)
            return stockfish_score
        
        finally:
            pass

    def evaluate_moves(self):# unused artifact
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
                adjusted_score = self.bias_scorer.move_bias_applicator(move, stockfish_score, self.board)
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

    def move_enters_visible_area(self, move):# unused artifact
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