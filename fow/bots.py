"""Reference bots. They see exactly what a submitted agent sees (the observation), nothing more.

    bot:random            uniform over legal moves
    bot:greedy            takes the most valuable visible piece, avoids squares visibly attacked
    bot:naive-sf          Stockfish on a board holding only the pieces it can see
                          (enemy king placed where it was last seen)
    bot:guess-sf-KxN      samples K full boards consistent with what it has seen, runs
                          Stockfish for N nodes on each, and plays the most-voted move

Stockfish is found through the STOCKFISH environment variable or `stockfish` on PATH.
"""
from __future__ import annotations

import os
import random
import re
import shutil

import chess
import chess.engine

from .memory import Memory, START_COUNT

LETTER_TYPE = {"P": chess.PAWN, "N": chess.KNIGHT, "B": chess.BISHOP, "R": chess.ROOK, "Q": chess.QUEEN, "K": chess.KING}
VALUE = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 100}


def stockfish_path() -> str:
    p = os.environ.get("STOCKFISH") or shutil.which("stockfish") or (
        "/usr/games/stockfish" if os.path.exists("/usr/games/stockfish") else None)
    if not p:
        raise RuntimeError("Stockfish not found: set STOCKFISH=/path/to/stockfish (see scripts/get_stockfish.sh)")
    return p


def visible_board(obs: dict) -> chess.Board:
    """Board with own pieces and visible enemy pieces only."""
    me = obs["color"] == "white"
    b = chess.Board(None)
    for sq, t in obs["own"].items():
        b.set_piece_at(chess.parse_square(sq), chess.Piece(LETTER_TYPE[t], me))
    for sq, t in obs["enemy"].items():
        b.set_piece_at(chess.parse_square(sq), chess.Piece(LETTER_TYPE[t], not me))
    b.turn = me
    return b


class Bot:
    name = "bot"

    def reset(self, color: str, seed: int) -> None:
        self.color = color
        self.rng = random.Random(seed)
        self.memory = Memory()

    def act(self, obs: dict) -> str:
        raise NotImplementedError

    def close(self) -> None:
        pass


class RandomBot(Bot):
    name = "bot:random"

    def act(self, obs):
        return self.rng.choice(obs["legal_moves"])


class GreedyBot(Bot):
    name = "bot:greedy"

    def act(self, obs):
        b = visible_board(obs)
        me = obs["color"] == "white"
        best, best_move = -1e9, None
        for mv in obs["legal_moves"]:
            to = mv[2:4]
            s = VALUE[obs["enemy"][to]] * 10 if to in obs["enemy"] else 0
            if b.is_attacked_by(not me, chess.parse_square(to)):
                s -= VALUE[obs["own"][mv[0:2]]] * 5
            s += self.rng.random()
            if s > best:
                best, best_move = s, mv
        return best_move


class StockfishBot(Bot):
    def __init__(self, samples: int = 1, nodes: int = 2000, guess: bool = False, name: str | None = None):
        self.samples, self.nodes, self.guess = samples, nodes, guess
        self.name = name or (f"bot:guess-sf-{samples}x{nodes}" if guess else "bot:naive-sf")
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path())
        self.engine.configure({"Threads": 1, "Hash": 16})

    def close(self):
        try:
            self.engine.quit()
        except Exception:
            pass

    def _sample_board(self, obs: dict) -> chess.Board | None:
        me = obs["color"] == "white"
        visible = set(obs["visible"])
        for _ in range(30):
            b = visible_board(obs)
            free = [s for s in chess.SQUARES if chess.square_name(s) not in visible and b.piece_at(s) is None]
            remaining = self.memory.remaining()
            for t in obs["enemy"].values():
                remaining[t] -= 1
            types = ["K"] * max(0, remaining["K"])
            if self.guess:
                for t in "QRBNP":
                    types += [t] * max(0, remaining[t])
            for t in types:
                spots = [chess.parse_square(s) for s, u in self.memory.last_seen.items()
                         if u == t and s not in visible and b.piece_at(chess.parse_square(s)) is None]
                sq = None
                if spots and (not self.guess or self.rng.random() < 0.7):
                    sq = self.rng.choice(spots)
                else:
                    cand = [s for s in free if b.piece_at(s) is None
                            and not (t == "P" and chess.square_rank(s) in (0, 7))]
                    if cand:
                        sq = self.rng.choice(cand)
                if sq is not None:
                    b.set_piece_at(sq, chess.Piece(LETTER_TYPE[t], not me))
            b.turn = me
            rights = 0
            if obs["castling"]["kingside"]:
                rights |= chess.BB_H1 if me else chess.BB_H8
            if obs["castling"]["queenside"]:
                rights |= chess.BB_A1 if me else chess.BB_A8
            b.castling_rights = rights
            if b.is_valid():
                return b
        return None

    def act(self, obs):
        self.memory.update(obs)
        legal = obs["legal_moves"]
        for mv in legal:                      # a visible king can be taken: the game is won
            if obs["enemy"].get(mv[2:4]) == "K":
                return mv
        votes: dict[str, int] = {}
        for _ in range(self.samples):
            b = self._sample_board(obs)
            if b is None:
                continue
            try:
                mv = self.engine.play(b, chess.engine.Limit(nodes=self.nodes)).move.uci()
            except Exception:
                continue
            if mv in legal:
                votes[mv] = votes.get(mv, 0) + 1
        if not votes:
            return GreedyBot.act(self, obs)
        return max(votes, key=lambda m: (votes[m], self.rng.random()))


def make_bot(spec: str) -> Bot:
    if spec == "bot:random":
        return RandomBot()
    if spec == "bot:greedy":
        return GreedyBot()
    if spec == "bot:naive-sf":
        return StockfishBot()
    m = re.fullmatch(r"bot:guess-sf-(\d+)x(\d+)", spec)
    if m:
        return StockfishBot(int(m.group(1)), int(m.group(2)), guess=True)
    raise ValueError(f"unknown bot {spec!r}")


# Ratings of the reference bots. The scale is fixed by bot:random = 0 and bot:greedy = 1000; the
# others are provisional, measured by the course staff with this code (600 games, round robin,
# 95% intervals about +-90), and will be re-measured in the tournaments.
REFERENCE_RATINGS: dict[str, float] = {
    "bot:random": 0.0,
    "bot:naive-sf": 920.0,
    "bot:greedy": 1000.0,
    "bot:guess-sf-4x500": 1060.0,
    "bot:guess-sf-16x1000": 1225.0,
}
