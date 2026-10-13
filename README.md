# Fog-of-War Chess: CSE 598 Final Project (Fall 2026)

Build the strongest agent you can for **Fog-of-War chess** (also called Dark Chess) with the
smallest model you can. Fog-of-War chess is chess in which you see only your own pieces and the
squares they can move to. There is no check; you win by capturing the king.

Agents play each other on a public ladder rated by Elo. Your agent's judgment must come from
neural networks totalling under 250M parameters, each move gets a fixed FLOP budget, and smaller
models get a rating bonus. The project runs from now until December, individually, and is worth 20 points of
your grade plus extra credit for the top 10 (see [docs/GRADING.md](docs/GRADING.md)).

## Why this game

Chess engines play far beyond human level, but only when they can see the board. Here they can't.

- **Stockfish is a limited teacher.** It can label the best move for the full board, which your
  agent never sees. Copying those moves runs into the hidden-information gap.
- **More engine compute barely helps.** Our reference bots that run Stockfish on boards guessed
  from what they have seen gain little from much more compute.
- **What it takes to go further:** memory, inferring where hidden pieces are, choosing what to
  reveal, playing unpredictably, and learning from self-play.

These are central problems in today's AI: learning from imperfect teachers, acting under
partial observability, and making models small and efficient.

## Quick start

```bash
# 1. your own private copy of this repository (see docs/COMPETITION.md), then:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[baseline]"

# 2. Stockfish (needed by some reference bots and to make training labels)
bash scripts/get_stockfish.sh            # prints the export line for STOCKFISH

# 3. play the baseline against the reference bots
python -m fow.arena agents/baseline bot:random bot:greedy bot:naive-sf bot:guess-sf-4x500 --games 40

# 4. check that your submission is valid
python -m fow.validate submission
```

On Sol, use `scripts/sol/setup_env.sh` once, then the job scripts in `scripts/sol/`.

## What is in this repository

| Path | What it is |
|---|---|
| [`docs/RULES.md`](docs/RULES.md) | the exact game rules |
| [`docs/COMPETITION.md`](docs/COMPETITION.md) | agent interface, observation format, limits, ladder, ratings, schedule |
| [`docs/POLICIES.md`](docs/POLICIES.md) | what is allowed at play and training time, compute, AI assistants, verification |
| [`docs/GRADING.md`](docs/GRADING.md) | milestones, rubric, extra credit |
| `fow/` | the rules engine, referee, reference bots, rating tools (`arena`, `validate`, `params`) |
| `agents/template/` | the smallest valid agent (random moves): the interface in 20 lines |
| `agents/baseline/` | the starting baseline (below) |
| `baselines/imitation/` | how the baseline was made: data generation and training |
| `submission/` | **your agent**; it starts as a copy of the baseline |
| `JOURNAL.md`, `AI_USE.md` | your project journal and AI disclosure |
| `scripts/` | Stockfish download and Sol job scripts |
| `tests/` | rule tests (`python -m pytest tests`) |

## The baseline

`agents/baseline` is a small residual CNN that plays without search.

- **Training:** it imitates the moves Stockfish picks when Stockfish can see the whole board.
- **Input:** what the agent sees now plus a memory of where it last saw each enemy piece.
- **Making it:**
  1. `baselines/imitation/generate_data.py` plays games between reference bots and labels
     positions with full-board Stockfish.
  2. `baselines/imitation/train.py` trains the network into an agent directory.

Local ratings from a 600-game round robin (40 games per pair, both colors, 95% intervals):

| Player | Rating | Notes |
|---|---:|---|
| `bot:guess-sf-16x1000` | 1225 | Stockfish voting over 16 guessed boards |
| **`agents/baseline`** | **1217** [1134, 1305] | 314,057 parameters, about 2 ms per move on one CPU core |
| `bot:guess-sf-4x500` | 1060 | Stockfish voting over 4 guessed boards |
| `bot:greedy` | 1000 | fixed: sets the scale |
| `bot:naive-sf` | 920 | Stockfish ignoring the fog |
| `bot:random` | 0 | fixed: sets the scale |

The baseline beats `bot:greedy` 33–7, `bot:naive-sf` 37–3 and `bot:random` 40–0, and splits
with `bot:guess-sf-16x1000` (17–23).

How much room is above it? In an early staff test, a Stockfish allowed to see the whole board
won all 160 of its games against the strongest bots and an earlier version of this baseline.
That isn't a reachable target, since it cheats, but the ceiling for fair Fog-of-War play is
far above this table.

It is meant to be beaten. Coding agents and a few hours can reproduce it. The interesting part is
everything it does not do: model the hidden pieces, go beyond its teacher, or get strong while
small.

## Key dates

| Date | |
|---|---|
| Fri Oct 30, 11:59 PM | proposal |
| Tue Nov 17, 11:59 PM | checkpoint |
| Fri Dec 4, 11:59 PM | model freeze |
| Dec 5–8 | final tournament |
| Sat Dec 12, 11:59 PM | final report and recorded presentation |

Weekly ladder runs start in early November; times and cutoffs are posted on Canvas.

## Questions

Ask on Canvas. If you find a bug in the rules engine or referee, open an issue in this
repository with a game seed that reproduces it.
