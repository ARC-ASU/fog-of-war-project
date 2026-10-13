"""The agent API in code form: the observation's fields and types, and a checker.

The full specification, with semantics and examples, is docs/API.md.
"""
from __future__ import annotations

from typing import Optional, TypedDict

API_VERSION = "1.0"
PIECE_LETTERS = set("PNBRQK")
SQUARES = {f + r for f in "abcdefgh" for r in "12345678"}


class Castling(TypedDict):
    kingside: bool
    queenside: bool


class Observation(TypedDict):
    api_version: str          # "1.0"
    variant: str              # "fow"
    color: str                # "white" or "black": the side to move, i.e. you
    ply: int                  # half-moves played so far in this game (0 at the start)
    own: dict[str, str]       # square -> piece letter, all of your pieces
    enemy: dict[str, str]     # square -> piece letter, enemy pieces on squares you can see
    visible: list[str]        # sorted list of squares you can see
    legal_moves: list[str]    # your legal moves in UCI (non-empty)
    castling: Castling        # your remaining castling rights
    last_move: Optional[str]  # the move you played last, or None
    lost_on: Optional[str]    # square where you lost a piece on the opponent's last move, or None


def check_observation(obs: dict) -> list[str]:
    """Return a list of problems (empty if the observation follows the specification)."""
    p = []
    expected = set(Observation.__annotations__)
    if set(obs) != expected:
        p.append(f"fields differ: missing {sorted(expected - set(obs))}, extra {sorted(set(obs) - expected)}")
        return p
    if obs["api_version"] != API_VERSION:
        p.append("api_version")
    if obs["variant"] != "fow":
        p.append("variant")
    if obs["color"] not in ("white", "black"):
        p.append("color")
    if not isinstance(obs["ply"], int) or obs["ply"] < 0:
        p.append("ply")
    for name in ("own", "enemy"):
        d = obs[name]
        if not all(s in SQUARES and t in PIECE_LETTERS for s, t in d.items()):
            p.append(name)
    if set(obs["own"]) & set(obs["enemy"]):
        p.append("own and enemy overlap")
    if obs["visible"] != sorted(obs["visible"]) or not set(obs["visible"]) <= SQUARES:
        p.append("visible")
    if not set(obs["own"]) <= set(obs["visible"]) or not set(obs["enemy"]) <= set(obs["visible"]):
        p.append("own/enemy squares must be visible")
    if not obs["legal_moves"] or not all(isinstance(m, str) and len(m) in (4, 5) for m in obs["legal_moves"]):
        p.append("legal_moves")
    if set(obs["castling"]) != {"kingside", "queenside"}:
        p.append("castling")
    for name in ("last_move", "lost_on"):
        if obs[name] is not None and not isinstance(obs[name], str):
            p.append(name)
    return p
