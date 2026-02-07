import chess

class ProbableStateAnalyzer:
    def __init__(self, BSL, engine, bias):
        self.BSL = BSL
        self.state_scores = len(self.BSL.board_states)#every possible board
        self.engine = engine
        self.board_scores = [(0, 46)] # initialize board_states
        self.bias = bias
    
    # Analyze each board state in BSL.board_states    
    def analyze_states(self):
        self.board_scores = []
        for i in range(len(self.BSL.board_states)):
            board = self.BSL.board_states[i]
            score = self.engine.board_state_analysis(board) #potentially use multiple engines
            # apply bias to possible states based on biased piece
            piece_to_counter = self.bias.get("piece", "")
            target_piece_type = board.piece_type_at(board.peek().to_square)
            if target_piece_type:
                target_piece_name = chess.PIECE_NAMES[target_piece_type].lower()
                if target_piece_name == piece_to_counter:  #if target is piece to counter
                    score += 50
            self.board_scores.append((i, score))
        self.board_scores.sort(key=lambda x: x[1], reverse=True) # Sort by score descending      