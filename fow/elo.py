"""Ratings from game results: a Bradley-Terry model on the Elo scale.

P(A beats B) = 1 / (1 + 10 ** ((R_B - R_A) / 400)); a draw counts as half a win for each side.
Players listed in `pinned` keep fixed ratings (the reference bots), so ratings from different
runs share one scale. 95% intervals come from resampling games (bootstrap).
"""
from __future__ import annotations

import math
import random


K = math.log(10) / 400.0
PRIOR_MEAN, PRIOR_SD = 1000.0, 1500.0   # very weak prior; only keeps all-win or all-loss players finite


def fit(games: list[tuple[str, str, float]], pinned: dict[str, float] | None = None,
        iters: int = 200) -> dict[str, float]:
    """games: (white, black, score for white). Returns name -> rating.
    Without pinned players, the first player alphabetically is set to 0."""
    pinned = dict(pinned or {})
    players = sorted({g[0] for g in games} | {g[1] for g in games})
    fixed = {p: v for p, v in pinned.items() if p in players} or {players[0]: 0.0}
    r = {p: fixed.get(p, PRIOR_MEAN) for p in players}
    by_player = {p: [] for p in players}
    for w, b, s in games:
        by_player[w].append((b, s))
        by_player[b].append((w, 1.0 - s))
    for _ in range(iters):
        delta = 0.0
        for p in players:
            if p in fixed:
                continue
            g = -(r[p] - PRIOR_MEAN) / PRIOR_SD ** 2
            h = -1.0 / PRIOR_SD ** 2
            for q, s in by_player[p]:
                e = 1.0 / (1.0 + math.exp(-K * (r[p] - r[q])))
                g += K * (s - e)
                h -= K * K * e * (1.0 - e)
            step = max(-400.0, min(400.0, -g / h))
            r[p] += step
            delta = max(delta, abs(step))
        if delta < 0.01:
            break
    return r


def fit_with_intervals(games, pinned=None, n_boot: int = 100, seed: int = 0):
    """Returns name -> (rating, low, high) with a 95% bootstrap interval."""
    point = fit(games, pinned)
    rng = random.Random(seed)
    samples = {p: [] for p in point}
    for _ in range(n_boot):
        bs = [games[rng.randrange(len(games))] for _ in games]
        r = fit(bs, pinned, iters=600)
        for p, v in r.items():
            samples[p].append(v)
    out = {}
    for p, v in point.items():
        s = sorted(samples[p]) or [v]
        out[p] = (v, s[int(0.025 * (len(s) - 1))], s[int(0.975 * (len(s) - 1))])
    return out


def size_adjusted(elo: float, params: int, beta: float, cap: int = 500_000_000, floor: int = 1_000_000) -> float:
    """Adjusted Elo = Elo + beta * log2(cap / max(params, floor)). beta is announced in docs/COMPETITION.md."""
    return elo + beta * math.log2(cap / max(params, floor))
