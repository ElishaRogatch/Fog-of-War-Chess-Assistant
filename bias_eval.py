import chess
from chess import SQUARES, Bitboard, BB_SQUARES

########BIAS EVALUATIONS NEEDS WORK
class BiasScorer:
    def __init__(self, bias):
        self.bias = bias  # The bias dictionary passed from the engine

    def move_bias_applicator(self, move, stockfish_score, board):
        """
        Adjusts the score of a move based on bias_dict for both White and Black.

        Parameters:
            move (chess.Move): The move being evaluated.
            stockfish_score (int): The base score provided by Stockfish.
            board (chess.Board): The board state to analyze the move.

        Returns:
            int: The adjusted score considering the bias.
        """
        if not self.bias:
            return stockfish_score  # No bias provided, return the Stockfish score as-is

        #values of each piece that can be changed from here
        pieces_value_dict = {
            "king" : 10,
            "queen" : 8,
            "bishop" : 5,
            "rook" : 5,
            "knight" : 3,
            "pawn" : 1
            }

        #Move Bias Applicator code
        piece_to_counter = self.bias.get("piece", "").lower() #the piece derived from the bias given
        counter_move_score = self.get_counter_move_score(move, board, piece_to_counter) * 50 #adds 50 score when the move targets the bias piece
        
        #maybe move line below to fow_engine to stop it from running each time
        vision_before_score = self.get_before_vision_score(board, pieces_value_dict)  #gets the vision state before to be used in determining the vision change
        vision_score = self.get_vision_score(move, board, pieces_value_dict, vision_before_score) #tends to return a negative score especially when the suggested move captures a piece
        
        if board.piece_at(move.to_square):
            vision_score += 10 #adds reward when move targets a piece to balance lost score for vision after
        
        risk_score = self.get_risk_score(move, board) * 10 #subtracts 10 score for each angle of attack exposed to with the passed move

        return stockfish_score + counter_move_score + vision_score - risk_score
    
    #TO FIX: all below functions use the actual board and not the prediction board currently
    def get_counter_move_score(self, move, board, piece_to_counter):
        #returns True if target location contains the bias piece
        target_piece_type = board.piece_type_at(move.to_square)
        if target_piece_type:
            target_piece_name = chess.PIECE_NAMES[target_piece_type].lower()
            return target_piece_name == piece_to_counter  #if target is piece to counter
        return False

    def get_before_vision_score(self, board, piece_value_dict): #this still gets run each time that move bias applicator is called. (Only needs to run once)
        #analyze vision state of board before move
        pieces_values = 0
        tile_value = 0
        visibility: Bitboard = board.get_fow_visibility()
        for square in SQUARES:
            if BB_SQUARES[square] & visibility:
                tile_value += 1
                piece = board.piece_type_at(square)
                color = board.color_at(square)
                if piece and not color: #only look at black pieces
                    piece_name = chess.PIECE_NAMES[piece].lower()
                    pieces_values += piece_value_dict[piece_name]
        vision_before = tile_value + pieces_values
        return vision_before

    def get_vision_score(self, move_to_make, board, piece_value_dict, vision_before):
        #analyze vision state of board after move
        board.push(move_to_make) #push move to make so that it can be analyzed
        board.push(chess.Move.null()) #push null move to make it white's turn
        pieces_values = 0
        tile_value = 0
        visibility: Bitboard = board.get_fow_visibility() 
        for square in SQUARES:
            if BB_SQUARES[square] & visibility:
                tile_value += 1
                piece = board.piece_type_at(square)
                color = board.color_at(square)
                if piece and not color: #only look at black pieces
                    piece_name = chess.PIECE_NAMES[piece].lower()
                    pieces_values += piece_value_dict[piece_name]
        board.pop() #undo null move
        board.pop() #undo move to make
        vision_after = tile_value + pieces_values
        return vision_after - vision_before

    def get_risk_score(self, move_to_make, board):
        #counts the number of black pieces that can attack the destination square
        angles_of_attack = board.attackers(False, move_to_make.to_square)
        return len(angles_of_attack)