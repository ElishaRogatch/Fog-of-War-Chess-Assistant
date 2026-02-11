"""Extension for chess to have FOW complient legal moves"""
from chess import *

# Mimic style of other legal move classes found in chess
class LegalFowMoveGenerator:

    def __init__(self, board: Board) -> None:
        self.board = board

    def __bool__(self) -> bool:
        return any(self.board.generate_fow_legal_moves())

    def count(self) -> int:
        # List conversion is faster than iterating.
        return len(list(self))

    def __iter__(self) -> Iterator[Move]:
        return self.board.generate_fow_legal_moves()

    def __contains__(self, move: Move) -> bool:
        return self.board.is_fow_legal(move)

    def __repr__(self) -> str:
        builder: List[str] = []

        for move in self:
            if self.board.is_legal(move):
                builder.append(self.board.san(move))
            else:
                builder.append(self.board.uci(move))

        sans = ", ".join(builder)
        return f"<LegalFowMoveGenerator at {id(self):#x} ({sans})>" 


class FowBoard(Board):
    """A child class of Board that implements the legal move changes that make the legal moves complient with fow chess rules"""
    uci_variant = "fow"
    
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stored_transposition_key = None
        
    @property
    def fow_legal_moves(self) -> LegalFowMoveGenerator:
        """
        A dynamic list of fow legal moves, much like the legal move list.

        fow moves might leave or put the king under attack, but are
        otherwise valid. Null moves are not fow legal. Castling moves are
        included even if the king passes through attacked squares.

        Wraps :func:`~chess.Board.generate_fow_legal_moves()` and
        :func:`~chess.Board.is_fow_legal()`.
        """
        return LegalFowMoveGenerator(self)

    # The same as is_pseudo_legal from chess with the exception of how the valid castle moves are generated
    def is_fow_legal(self, move: Move) -> bool:
            # Null moves are not pseudo-legal.
            if not move:
                return False

            # Drops are not pseudo-legal.
            if move.drop:
                return False

            # Source square must not be vacant.
            piece = self.piece_type_at(move.from_square)
            if not piece:
                return False

            # Get square masks.
            from_mask = BB_SQUARES[move.from_square]
            to_mask = BB_SQUARES[move.to_square]

            # Check turn.
            if not self.occupied_co[self.turn] & from_mask:
                return False

            # Only pawns can promote and only on the backrank.
            if move.promotion:
                if piece != PAWN:
                    return False

                if self.turn == WHITE and square_rank(move.to_square) != 7:
                    return False
                elif self.turn == BLACK and square_rank(move.to_square) != 0:
                    return False

            # Handle castling.
            if piece == KING:
                move = self._from_chess960(self.chess960, move.from_square, move.to_square)
                if move in self.generate_fow_castling_moves():
                    return True

            # Destination square can not be occupied.
            if self.occupied_co[self.turn] & to_mask:
                return False

            # Handle pawn moves.
            if piece == PAWN:
                return move in self.generate_fow_legal_moves(from_mask, to_mask)

            # Handle all other pieces.
            return bool(self.attacks_mask(move.from_square) & to_mask)
        
    #The same as generate_pseudo_legal_moves from chess with the exception of how the valid castle moves are generated   
    def generate_fow_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
            our_pieces = self.occupied_co[self.turn]

            # Generate piece moves.
            non_pawns = our_pieces & ~self.pawns & from_mask
            for from_square in scan_reversed(non_pawns):
                moves = self.attacks_mask(from_square) & ~our_pieces & to_mask
                for to_square in scan_reversed(moves):
                    yield Move(from_square, to_square)

            # Generate castling moves.
            if from_mask & self.kings:
                yield from self.generate_fow_castling_moves(from_mask, to_mask)

            # The remaining moves are all pawn moves.
            pawns = self.pawns & self.occupied_co[self.turn] & from_mask
            if not pawns:
                return

            # Generate pawn captures.
            capturers = pawns
            for from_square in scan_reversed(capturers):
                targets = (
                    BB_PAWN_ATTACKS[self.turn][from_square] &
                    self.occupied_co[not self.turn] & to_mask)

                for to_square in scan_reversed(targets):
                    if square_rank(to_square) in [0, 7]:
                        yield Move(from_square, to_square, QUEEN)
                        yield Move(from_square, to_square, ROOK)
                        yield Move(from_square, to_square, BISHOP)
                        yield Move(from_square, to_square, KNIGHT)
                    else:
                        yield Move(from_square, to_square)

            # Prepare pawn advance generation.
            if self.turn == WHITE:
                single_moves = pawns << 8 & ~self.occupied
                double_moves = single_moves << 8 & ~self.occupied & (BB_RANK_3 | BB_RANK_4)
            else:
                single_moves = pawns >> 8 & ~self.occupied
                double_moves = single_moves >> 8 & ~self.occupied & (BB_RANK_6 | BB_RANK_5)

            single_moves &= to_mask
            double_moves &= to_mask

            # Generate single pawn moves.
            for to_square in scan_reversed(single_moves):
                from_square = to_square + (8 if self.turn == BLACK else -8)

                if square_rank(to_square) in [0, 7]:
                    yield Move(from_square, to_square, QUEEN)
                    yield Move(from_square, to_square, ROOK)
                    yield Move(from_square, to_square, BISHOP)
                    yield Move(from_square, to_square, KNIGHT)
                else:
                    yield Move(from_square, to_square)

            # Generate double pawn moves.
            for to_square in scan_reversed(double_moves):
                from_square = to_square + (16 if self.turn == BLACK else -16)
                yield Move(from_square, to_square)

            # Generate en passant captures.
            if self.ep_square:
                yield from self.generate_pseudo_legal_ep(from_mask, to_mask)

    # The same as generate_castling_moves from chess with the exception of allowing castling through "check" as it is a fow legal move
    def generate_fow_castling_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        if self.is_variant_end():
            return

        backrank = BB_RANK_1 if self.turn == WHITE else BB_RANK_8
        king = self.occupied_co[self.turn] & self.kings & ~self.promoted & backrank & from_mask
        king &= -king
        if not king:
            return

        bb_c = BB_FILE_C & backrank
        bb_d = BB_FILE_D & backrank
        bb_f = BB_FILE_F & backrank
        bb_g = BB_FILE_G & backrank

        for candidate in scan_reversed(self.clean_castling_rights() & backrank & to_mask):
            rook = BB_SQUARES[candidate]

            a_side = rook < king
            king_to = bb_c if a_side else bb_g
            rook_to = bb_d if a_side else bb_f

            king_path = between(msb(king), msb(king_to))
            rook_path = between(candidate, msb(rook_to))

            if not (self.occupied ^ king ^ rook) & (king_path | rook_path | king_to | rook_to):
                yield self._from_chess960(self.chess960, msb(king), candidate)
      
    # Modified version of outcome function that makes draws manditory if possible and doesn't check regular chess end conditions          
    def outcome(self) -> Optional[Outcome]:
        """
        Check if the game is over due to,
        the :func:`fifty-move rule <chess.Board.is_fifty_moves()>`,
        :func:`threefold repetition <chess.Board.is_repetition()>`,
        or a :func:`variant end condition <chess.Board.is_variant_end()>`.
        Returns the :class:`chess.Outcome` if the game has ended, otherwise
        ``None``.
        """
        # Variant support.
        if self.is_variant_loss():
            return Outcome(Termination.VARIANT_LOSS, not self.turn)
        if self.is_variant_win():
            return Outcome(Termination.VARIANT_WIN, self.turn)
        if self.is_variant_draw():
            return Outcome(Termination.VARIANT_DRAW, None)

        # Automatic draws.
        if self.is_fifty_moves():
            return Outcome(Termination.FIFTY_MOVES, None)
        if self.is_repetition():
            return Outcome(Termination.THREEFOLD_REPETITION, None)
        
        return None
    
    def is_variant_loss(self) -> bool:
        """
        Checks if the current side to move lost due to a variant-specific
        condition.
        """
        if not self.pieces_mask(KING, self.turn): # if no king is found in your pieces you lose
            return True
        return False
    
    # Modified version of parse_uci function that sees if the move is fow_legal not regular legal, and prevents engine errors
    def parse_uci(self, uci: str) -> Move:
        """
        Parses the given move in UCI notation.

        Supports both Chess960 and standard UCI notation.

        The returned move is guaranteed to be either legal or a null move.

        :raises:
            :exc:`ValueError` (specifically an exception specified below) if the move is invalid or illegal in the
            current position (but not a null move).

            - :exc:`InvalidMoveError` if the UCI is syntactically invalid.
            - :exc:`IllegalMoveError` if the UCI is illegal.
        """
        move = Move.from_uci(uci)

        if not move:
            return move

        move = self._to_chess960(move)
        move = self._from_chess960(self.chess960, move.from_square, move.to_square, move.promotion, move.drop)

        if not self.is_fow_legal(move):
            raise IllegalMoveError(f"illegal uci: {uci!r} in {self.fen()}")

        return move
    
    def get_fow_visibility(self) -> Bitboard:
        """Gets the visibility mask for the player to move"""
        move_squares = [move.to_square for move in self.fow_legal_moves]
        move_to = BB_EMPTY
        for square in move_squares:
            move_to = move_to | BB_SQUARES[square]
        return self.occupied_co[self.turn] | move_to
    
    def get_semi_visibility(self, visible : Bitboard) -> Bitboard:
        """Gets the semi visibility mask for the player to move. This is based on the pawn moves that are/aren't availiable."""
        attack_moves = BB_EMPTY
        single_moves = BB_EMPTY
        double_moves = BB_EMPTY
        pawns = self.pieces_mask(PAWN, self.turn)
        
        # finds the squares you would see if you were able to attack, thus implying that they are safe
        for from_square in scan_reversed(pawns):
            attack_moves = attack_moves | BB_PAWN_ATTACKS[self.turn][from_square] 
        attack_moves = attack_moves & ~visible
        
        # find the squares you would see if you were able to move there, thus implying that they have a piece there
        if self.turn == WHITE:
            single_moves = pawns << 8
            double_moves = (pawns << 16) & BB_RANK_4
        else:
            single_moves = pawns >> 8
            double_moves = (pawns >> 16) & BB_RANK_5
        single_moves = single_moves & ~visible
        double_moves = double_moves & ~visible
        # only include a double move if the single move is empty
        if self.turn == WHITE:
            double_moves = double_moves & ~(single_moves << 8) & ~(self.occupied << 8)
        else:
            double_moves = double_moves & ~(single_moves >> 8) & ~(self.occupied >> 8)
        return attack_moves | single_moves | double_moves
        
    def get_ep_visibility(self, visible) -> Bitboard:
        """Gets the ep visibility mask for the player to move."""
        ep_visible = BB_EMPTY
        if self.ep_square and visible & BB_SQUARES[self.ep_square]:
            if self.turn == WHITE:
                ep_visible = BB_SQUARES[self.ep_square - 8]
            else:
                ep_visible = BB_SQUARES[self.ep_square + 8]
        return ep_visible