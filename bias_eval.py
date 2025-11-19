import chess
from chess import SQUARES, Bitboard, BB_SQUARES

########BIAS EVALUATIONS NEEDS WORK
class BiasScorer:
    def __init__(self, bias):
        self.bias = bias  # The bias dictionary passed from the engine
        self.piece_value_dict = {
            "king" : 10,
            "queen" : 8,
            "bishop" : 5,
            "rook" : 5,
            "knight" : 3,
            "pawn" : 1
            }

    def move_bias_applicator(self, move, stockfish_score, board, vision_before_score):
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
        

        #Move Bias Applicator code
        piece_to_counter = self.bias.get("piece", "") #the piece derived from the bias given
        counter_move_score = self.get_counter_move_score(move, board, piece_to_counter) * 50 #adds 50 score when the move targets the bias piece
        
        vision_score = self.get_vision_score(move, board, vision_before_score) #tends to return a negative score especially when the suggested move captures a piece
        
        if board.piece_at(move.to_square):
            vision_score += 10 #adds reward when move targets a piece to balance lost score for vision after
        
        #risk_score = self.get_risk_score(move, board) * 10 #subtracts 10 score for each angle of attack exposed to with the passed move
        risk_score = 0
        return stockfish_score + counter_move_score + vision_score - risk_score
    
    #TO FIX: all below functions use the actual board and not the prediction board currently
    def get_counter_move_score(self, move, board, piece_to_counter):
        #returns True if target location contains the bias piece
        target_piece_type = board.piece_type_at(move.to_square)
        if target_piece_type:
            target_piece_name = chess.PIECE_NAMES[target_piece_type].lower()
            return target_piece_name == piece_to_counter  #if target is piece to counter
        return False

    def get_before_vision_score(self, board): #this still gets run each time that move bias applicator is called. (Only needs to run once)
        #analyze vision state of board before move
        piece_values = 0
        visibility: Bitboard = board.get_fow_visibility()
        tile_value = visibility.bit_count()
        visible_opponent = visibility & board.occupied_co[not board.turn]
        piece_values += self.piece_value_dict["pawn"] * (visible_opponent & board.pawns).bit_count()
        piece_values += self.piece_value_dict["knight"] * (visible_opponent & board.knights).bit_count()
        piece_values += self.piece_value_dict["bishop"] * (visible_opponent & board.bishops).bit_count()
        piece_values += self.piece_value_dict["rook"] * (visible_opponent & board.rooks).bit_count()
        piece_values += self.piece_value_dict["queen"] * (visible_opponent & board.queens).bit_count()
        piece_values += self.piece_value_dict["king"] * (visible_opponent & board.kings).bit_count()
        vision_before = tile_value + piece_values
        return vision_before

    def get_vision_score(self, move_to_make, board, vision_before):
        #analyze vision state of board after move
        board.push(move_to_make) #push move to make so that it can be analyzed
        board.push(chess.Move.null()) #push null move to make it white's turn
        piece_values = 0
        visibility: Bitboard = board.get_fow_visibility() 
        tile_value = visibility.bit_count()
        visible_opponent = visibility & board.occupied_co[not board.turn]
        piece_values += self.piece_value_dict["pawn"] * (visible_opponent & board.pawns).bit_count()
        piece_values += self.piece_value_dict["knight"] * (visible_opponent & board.knights).bit_count()
        piece_values += self.piece_value_dict["bishop"] * (visible_opponent & board.bishops).bit_count()
        piece_values += self.piece_value_dict["rook"] * (visible_opponent & board.rooks).bit_count()
        piece_values += self.piece_value_dict["queen"] * (visible_opponent & board.queens).bit_count()
        piece_values += self.piece_value_dict["king"] * (visible_opponent & board.kings).bit_count()
        board.pop() #undo null move
        board.pop() #undo move to make
        vision_after = tile_value + piece_values
        return vision_after - vision_before

    def get_risk_score(self, move_to_make, board):
        #counts the number of black pieces that can attack the destination square
        angles_of_attack = board.attackers(False, move_to_make.to_square)
        return len(angles_of_attack)