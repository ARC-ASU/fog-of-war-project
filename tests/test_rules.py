import chess
import pytest

from fow.game import Game, legal_moves
from fow.elo import fit, size_adjusted
from fow.memory import Memory


def test_start_observation_hides_enemy():
    g = Game()
    g.play("e2e4")
    obs = g.observation()
    assert obs["color"] == "black"
    assert obs["enemy"] == {}
    assert "e4" not in obs["visible"]
    assert {"a6", "a5", "c6", "f6", "h6"} <= set(obs["visible"])
    assert obs["last_move"] is None and obs["lost_on"] is None


def test_castling_through_attack_is_legal():
    b = chess.Board("r3k2r/8/8/8/8/8/5q2/R3K2R w KQkq - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" in moves and "e1c1" in moves


def test_castling_needs_empty_squares():
    b = chess.Board("r3k2r/8/8/8/8/8/8/RN2K1NR w KQkq - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" not in moves and "e1c1" not in moves


def test_leaving_king_attacked_is_legal_and_king_capture_wins():
    g = Game()
    for mv in ["e2e4", "f7f6", "d1h5"]:      # the queen now attacks e8; nothing warns Black
        g.play(mv)
    assert "a7a6" in g.legal_uci()           # Black may ignore the attack
    g.play("a7a6")
    assert g.observation()["enemy"].get("e8") == "K"
    g.play("h5e8")
    assert g.over and g.result == "1-0" and g.termination == "king captured"
    assert g.score("white") == 1.0 and g.score("black") == 0.0


def test_lost_on_and_last_move():
    g = Game()
    for mv in ["e2e4", "d7d5", "e4d5"]:
        g.play(mv)
    obs = g.observation()
    assert obs["lost_on"] == "d5" and obs["last_move"] == "d7d5"


def test_illegal_move_raises():
    g = Game()
    with pytest.raises(ValueError):
        g.play("e2e5")


def test_promotions_listed():
    b = chess.Board("8/P6k/8/8/8/8/8/K7 w - - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert {"a7a8q", "a7a8n", "a7a8r", "a7a8b"} <= moves


def test_memory_counts_captures():
    g = Game()
    mem = Memory()
    for mv in ["e2e4", "d7d5"]:
        g.play(mv)
    obs = g.observation()
    mem.update(obs)
    assert obs["enemy"] == {"d5": "P"}
    g.play("e4d5")
    g.play("a7a6")
    mem.update(g.observation())
    assert mem.captured["P"] == 1


def test_elo_fit_orders_players():
    games = [("a", "b", 1.0)] * 30 + [("b", "a", 0.0)] * 30 + [("b", "c", 1.0)] * 20 + [("c", "b", 0.5)] * 20
    r = fit(games, {"c": 0.0})
    assert r["a"] > r["b"] > r["c"] == 0.0


def test_size_adjustment():
    assert size_adjusted(1000, 500_000_000, 50) == 1000
    assert abs(size_adjusted(1000, 1_000, 50) - (1000 + 50 * 8.965784284662087)) < 1e-6
