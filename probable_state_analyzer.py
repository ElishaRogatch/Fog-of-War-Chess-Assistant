import chess

class ProbableStateAnalyzer:
    def __init__(self, BSL, engine):
        self.BSL = BSL
        self.state_scores = len(self.BSL.board_states)#every possible board
        self.engine = engine
    
    # Analyze each board state in BSL.board_states    
    def analyze_states(self):
        scores = {}
        for i in range(len(self.BSL.board_states)):
            board = self.BSL.board_states[i]
            score = self.engine.board_state_analysis(board) #potentially use multiple engines
            scores[score] = i
        scores = sorted(scores.items())
        return scores #(score, index)        