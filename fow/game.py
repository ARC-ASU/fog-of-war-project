"""Fog-of-War chess rules. This module is the reference implementation: if it disagrees with
docs/RULES.md, report it; until fixed, this code decides official games.

Rules in brief
- Normal chess piece moves, but there is no check: you may move into or stay in check.
- You win by capturing the opponent's king.
- Castling needs only the castling right and empty squares between king and rook;
  attacked squares do not matter.
- You see your own pieces and every square one of your legal moves lands on
  (plus the pawn an en-passant capture would remove).
- Draw: 100 plies in a row without a capture or pawn move, 400 plies in total,
  or the side to move has no legal move.
"""
from __future__ import annotations

import chess

MAX_PLIES = 400
QUIET_PLIES = 100

PIECE_LETTER = {chess.PAWN: "P", chess.KNIGHT: "N", chess.BISHOP: "B",
                chess.ROOK: "R", chess.QUEEN: "Q", chess.KING: "K"}


def legal_moves(board: chess.Board) -> list[chess.Move]:
    """Legal moves for the side to move under Fog-of-War rules."""
    moves = [m for m in board.generate_pseudo_legal_moves() if not board.is_castling(m)]
    color = board.turn
    rank = 0 if color == chess.WHITE else 7
    king_sq = chess.square(4, rank)
    if board.piece_at(king_sq) == chess.Piece(chess.KING, color):
        for rook_file, king_to, between in ((7, 6, (5, 6)), (0, 2, (1, 2, 3))):
            rook_sq = chess.square(rook_file, rank)
            if (board.castling_rights & chess.BB_SQUARES[rook_sq]
                    and board.piece_at(rook_sq) == chess.Piece(chess.ROOK, color)
                    and all(board.piece_at(chess.square(f, rank)) is None for f in between)):
                moves.append(chess.Move(king_sq, chess.square(king_to, rank)))
    return moves


class Game:
    """One Fog-of-War game. The referee owns the Game; agents only ever see observations."""

    def __init__(self) -> None:
        self.board = chess.Board()
        self.quiet = 0
        self.result: str | None = None      # "1-0", "0-1", "1/2-1/2"
        self.termination: str | None = None
        self.moves: list[str] = []
        self.lost_on: dict[bool, str | None] = {chess.WHITE: None, chess.BLACK: None}
        self.last_move: dict[bool, str | None] = {chess.WHITE: None, chess.BLACK: None}
        self._legal = legal_moves(self.board)
        self._check_draw()

    @property
    def turn(self) -> str:
        return "white" if self.board.turn == chess.WHITE else "black"

    @property
    def over(self) -> bool:
        return self.result is not None

    def legal_uci(self) -> list[str]:
        return [m.uci() for m in self._legal]

    def observation(self) -> dict:
        """What the side to move is allowed to know (JSON-serializable)."""
        b = self.board
        c = b.turn
        visible = set(chess.SquareSet(b.occupied_co[c]))
        for m in self._legal:
            visible.add(m.to_square)
            if b.is_en_passant(m):
                visible.add(m.to_square + (-8 if c == chess.WHITE else 8))
        own = {chess.square_name(s): PIECE_LETTER[b.piece_type_at(s)] for s in chess.SquareSet(b.occupied_co[c])}
        enemy = {chess.square_name(s): PIECE_LETTER[b.piece_type_at(s)]
                 for s in visible if b.color_at(s) == (not c)}
        rank_bb = chess.BB_RANK_1 if c == chess.WHITE else chess.BB_RANK_8
        rights = b.castling_rights & rank_bb
        return {
            "color": self.turn,
            "ply": b.ply(),
            "own": own,
            "enemy": enemy,
            "visible": sorted(chess.square_name(s) for s in visible),
            "legal_moves": self.legal_uci(),
            "castling": {"kingside": bool(rights & chess.BB_FILE_H), "queenside": bool(rights & chess.BB_FILE_A)},
            "last_move": self.last_move[c],
            "lost_on": self.lost_on[c],
        }

    def play(self, uci: str) -> None:
        """Apply a move for the side to move. Raises ValueError if it is not legal."""
        if self.over:
            raise ValueError("game is over")
        move = chess.Move.from_uci(uci)
        if move not in self._legal:
            raise ValueError(f"illegal move {uci}")
        b = self.board
        mover = b.turn
        captured = b.piece_type_at(move.to_square)
        captured_sq = move.to_square
        if b.is_en_passant(move):
            captured = chess.PAWN
            captured_sq = move.to_square + (-8 if mover == chess.WHITE else 8)
        pawn_move = b.piece_type_at(move.from_square) == chess.PAWN
        b.push(move)
        self.moves.append(uci)
        self.last_move[mover] = uci
        self.lost_on[not mover] = chess.square_name(captured_sq) if captured else None
        self.quiet = 0 if (captured or pawn_move) else self.quiet + 1
        if captured == chess.KING:
            self.result = "1-0" if mover == chess.WHITE else "0-1"
            self.termination = "king captured"
            return
        self._legal = legal_moves(b)
        self._check_draw()

    def forfeit(self, color: str, reason: str) -> None:
        self.result = "0-1" if color == "white" else "1-0"
        self.termination = reason

    def _check_draw(self) -> None:
        if not self._legal:
            self.result, self.termination = "1/2-1/2", "no legal move"
        elif self.board.ply() >= MAX_PLIES:
            self.result, self.termination = "1/2-1/2", f"{MAX_PLIES} plies"
        elif self.quiet >= QUIET_PLIES:
            self.result, self.termination = "1/2-1/2", f"{QUIET_PLIES} plies without capture or pawn move"

    def score(self, color: str) -> float:
        """1, 0.5 or 0 for `color` once the game is over."""
        if self.result == "1/2-1/2":
            return 0.5
        white_won = self.result == "1-0"
        return 1.0 if (white_won == (color == "white")) else 0.0
