import chess

class ProbableStateAnalyzer:
    def __init__(self, BSL, engine):
        self.BSL = BSL
        self.state_scores = len(self.BSL.board_states)#every possible board
        self.engine = engine
        self.board_scores = [(0, 46)] # initialize board_states
    
    # Analyze each board state in BSL.board_states    
    def analyze_states(self):
        self.board_scores = []
        for i in range(len(self.BSL.board_states)):
            board = self.BSL.board_states[i]
            score = self.engine.board_state_analysis(board) #potentially use multiple engines
            self.board_scores.append((i, score))
        self.board_scores.sort(key=lambda x: x[1], reverse=True) # Sort by score descending       