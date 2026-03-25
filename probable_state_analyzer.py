import chess

class ProbableStateAnalyzer:
    def __init__(self, BSL, engine, biases):
        self.BSL = BSL
        self.state_scores = len(self.BSL.board_states)#every possible board
        self.engine = engine
        self.board_scores = [(0, 46)] # initialize board_states
        self.biases = biases
    
    # Analyze each board state in BSL.board_states    
    def analyze_states(self):
        self.board_scores = []
        for i in range(len(self.BSL.board_states)):
            board = self.BSL.board_states[i]
            score = self.engine.board_state_analysis(board) #potentially use multiple engines
            # apply bias to possible states based on biased piece
            for bias in self.biases:
                piece_to_counter = bias
                target_pieces = [chess.PIECE_NAMES[piece_type] for piece_type in board.last_piece_moved]
                piece_chance = target_pieces.count(piece_to_counter) / len(target_pieces) #the chance that the target
                score += 50 * piece_chance * self.biases[bias]
            self.board_scores.append((i, score))
        self.board_scores.sort(key=lambda x: x[1], reverse=True) # Sort by score descending   
    
    

    