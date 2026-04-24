from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_chess import FowBoard
    from chess import Bitboard
    
import chess
import copy


class BoardStateLimiter:
    def __init__(self, board: FowBoard, board_states: list[FowBoard]):
        self.board = board
        self.board_states = board_states
    
    def post_move_limiting(self):
        """Update the possible boardstates to reflect the assisted player's move and remove contradicting boardstates"""
        # make the known move for all potential states
        for boardstate in self.board_states:
            boardstate.push(self.board.peek())
        self.board.push(chess.Move.null()) # temporary move for the otherside so the legal move generator can see from correct pov
        self.board_states[:] = self._remove_contradicting_states(self.board_states)
        self.board.pop() # undo temp move
        
    def pre_move_limiting(self):
        """For each boardstate find all possible legal moves and create a new state for each possible move being made and 
        remove contradincting and duplicate boardstates."""
        new_board_states: list[FowBoard] = []
        for boardstate in self.board_states:
            for move in boardstate.fow_legal_moves:
                new_boardstate = copy.copy(boardstate)
                new_boardstate.push(move)
                # check to make sure that if a capture occurs the potential states reflect that
                if self.board.occupied_co[self.board.turn] != new_boardstate.occupied_co[new_boardstate.turn]:
                    continue
                # check to make sure new state isnt a duplicate
                new_boardstate.stored_transposition_key = new_boardstate._transposition_key()
                new_boardstate.last_piece_moved = [new_boardstate.piece_type_at(new_boardstate.peek().to_square)]
                is_duplicate, duplicate_state = self._is_duplicate_state(new_boardstate, new_board_states)
                if not is_duplicate:
                    new_board_states.append(new_boardstate)
                else:
                    duplicate_state.last_piece_moved.append(new_boardstate.last_piece_moved[0])
        # in new states generation check for captures by checking piece mask of the side about to move
        new_board_states[:] = self._remove_contradicting_states(new_board_states)
        # make new states the old states (for next move)
        self.board_states = new_board_states
    
    def _does_match_visibility(self, board1: FowBoard, board2: FowBoard, visible: Bitboard, semi_visible: Bitboard) -> bool:
        if ~board1.occupied & (visible | semi_visible) != ~board2.occupied & (visible | semi_visible): # empty squares don't match
            return False
        elif board1.pawns & visible != board2.pawns & visible: # visible pawns don't match
            return False
        elif board1.knights & visible != board2.knights & visible: # visible knights don't match
            return False
        elif board1.bishops & visible != board2.bishops & visible: # visible bishops don't match
            return False
        elif board1.rooks & visible != board2.rooks & visible: # visible rooks don't match
            return False
        elif board1.queens & visible != board2.queens & visible: # visible queens don't match
            return False
        elif board1.kings & visible != board2.kings & visible: # visible kings don't match
            return False
        else:
            return True
     
    def _remove_contradicting_states(self, boardstates: list[FowBoard]) -> list[FowBoard]:
        visible: Bitboard = self.board.get_fow_visibility()
        visible = visible | self.board.get_ep_visibility()
        semi_visible: Bitboard = self.board.get_semi_visibility(visible)
        # remove any states that contradict visible observations
        return [boardstate for boardstate in boardstates if self._does_match_visibility(self.board, boardstate, visible, semi_visible)]
       
    def _is_duplicate_state(self, boardstate: FowBoard, boardstates: list[FowBoard]) -> tuple[bool, FowBoard | None]:
        for unique_boardstate in boardstates:
            # use transposition key rather than just '==' to limit the states by not concerning over differences in the half-move count between states
            if boardstate.stored_transposition_key == unique_boardstate.stored_transposition_key:
                return True, unique_boardstate
        return False, None