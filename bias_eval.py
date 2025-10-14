import chess

########BIAS EVALUATIONS NEEDS WORK
class BiasScorer:
    def __init__(self, bias):
        self.bias = bias  # The bias dictionary passed from the engine

    def get_bias_score(self, move, stockfish_score, board, is_black_turn):
        """
        Adjusts the score of a move based on bias_dict for both White and Black.

        Parameters:
            move (chess.Move): The move being evaluated.
            stockfish_score (int): The base score provided by Stockfish.
            board (chess.Board): The board state to analyze the move.
            is_black_turn (bool): True if evaluating Black's moves, False if evaluating White's.

        Returns:
            int: The adjusted score considering the bias.
        """
        if not self.bias:
            return stockfish_score  # No bias provided, return the Stockfish score as-is

        bias_score = stockfish_score  # Start with the base Stockfish score

        # Retrieve bias parameters
        severity = self.bias.get("severity", 1)
        piece = self.bias.get("piece", "").lower()
        action = self.bias.get("action", "").lower()
        preference = self.bias.get("preference", False)
        force_forks = self.bias.get("force forks", False)

        # Retrieve the piece type making the move
        piece_type = board.piece_type_at(move.from_square)
        piece_name = chess.PIECE_NAMES[piece_type] if piece_type else ""

        if is_black_turn:
            # Boost Black's moves that align with the perceived strategy
            if piece_name.lower() == piece:
                bias_score += 10 * severity
            if force_forks and self.move_creates_fork(move, board):
                bias_score += 15 * severity
            if preference and piece_name.lower() == piece:
                bias_score += 5

        else:
            # Boost White's moves that counter Black's strategy
            if action == "punish" and self.is_punishing_move(move, board, piece, is_black_turn):
                bias_score += 10 * severity  # Countering Black's overuse of a piece

            if action == "counter" and self.is_counter_move(move, board):
                bias_score += 8 * severity  # Defensive moves that counter Black's attacks

            if action == "attack" and board.is_capture(move) and piece_name.lower() == piece:
                bias_score += 10 * severity  # Capturing Black's favored piece

        return bias_score


    def move_creates_fork(self, move, board):
        board.push(move)
        attackers = board.attackers(not board.turn, move.to_square)
        board.pop()
        return len(attackers) > 1

    def is_punishing_move(self, move, board, piece, is_black_turn):
        target_piece = board.piece_at(move.to_square)
        if target_piece:
            target_piece_name = chess.PIECE_NAMES[target_piece.piece_type].lower()
            return target_piece_name == piece
        return False

    def is_counter_move(self, move, board):
        board.push(move)
        is_counter = board.is_check()  # This needs work
        board.pop()
        return is_counter