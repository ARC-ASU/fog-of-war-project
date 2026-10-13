# Fog-of-War Chess: CSE 598 Final Project (Fall 2026)

> **Your task:** train a small neural network that plays chess when it can't see most of the board.
> Agents play each other in two tournaments, and the strongest small models win.

- **Individual project**, 20 points of your grade, plus extra credit for the top 10.
- **Proposal** Fri Oct 23 · **pre-tournament entry** Tue Nov 17 · **final entry** Fri Dec 4 · **report and video** Sat Dec 12.

---

## 1. The game in one minute

Fog-of-War chess (also called Dark Chess) is ordinary chess with one twist: **you only see your
own pieces and the squares they can move to.** Everything else is hidden.

Here is what White sees after `1. e4 d5`:

```
8   ? ? ? ? ? ? ? ?        ?  hidden
7   ? ? ? ? ? ? ? ?        .  empty square you can see
6   . ? ? ? ? ? ? ?        p  an enemy piece you can see
5   ? . ? p . ? ? .
4   . . . . P . . .
3   . . . . ? . . .
2   P P P P . P P P
1   R N B Q K B N R
    a b c d e f g h
```

- White sees Black's pawn on d5 only because the e4 pawn could capture it.
- Every other black piece is hidden.

Two more differences from normal chess:

1. **There is no check.** Nothing warns you when your king is attacked, and you may move into danger.
2. **You win by capturing the king.**

The exact rules are in [docs/RULES.md](docs/RULES.md). To get a feel for the game, try it
yourself first; see [Learn the game](#6-learn-the-game).

## 2. Why this is a good deep-learning problem

Chess engines like Stockfish play far beyond human level, **but only when they can see the
whole board**. Here, they can't.

- **Stockfish is only a partial teacher.** It can tell you the best move for the full board, a
  board your agent never sees.
- **More engine compute barely helps.** Our Stockfish-based reference bots improve very little
  when given much more search.
- **Getting good takes what modern AI work is about:** remembering what you've seen, inferring
  what you can't see, learning beyond your teacher (self-play, RL), and doing it with a small,
  efficient model.

## 3. What you build, and the rules at a glance

You write `submission/agent.py`: given what your side can see, return a move. The exact
interface is in [docs/API.md](docs/API.md). Inside, you design everything: memory, belief about
hidden pieces, search with your own networks, sampling.

| Rule | In short | Details |
|---|---|---|
| Neural networks only | Your agent's judgment comes from neural networks you train. Several are allowed. | [COMPETITION](docs/COMPETITION.md#core-models) |
| Size | Under **250M parameters** in total; smaller models get a rating bonus | [COMPETITION](docs/COMPETITION.md#size-adjusted-rating) |
| Compute | At most **10¹² FLOPs per move**, counted automatically, the same on any machine | [COMPETITION](docs/COMPETITION.md#how-compute-is-counted) |
| No engines at play time | No Stockfish or hand-written evaluation inside your agent. Engines **are** allowed as teachers during training. | [POLICIES](docs/POLICIES.md) |
| Work in the open | Commit and push often; each commit is one clear step, and your journal records every experiment | [POLICIES](docs/POLICIES.md#your-repository-and-commit-history) |
| Replicable from scratch | The staff rerun every entry's training from your `REPRODUCE.md` and `reproduce.sh`. It must produce a similar model within the replication budget, or it is an integrity violation. | [POLICIES](docs/POLICIES.md#documentation-and-end-to-end-replication) |
| AI assistants | Allowed and encouraged, with disclosure | [POLICIES](docs/POLICIES.md#ai-assistants), [RESOURCES](docs/RESOURCES.md) |

Ratings are Elo from tournament games, and rankings use **size-adjusted** Elo.

- **The pre-tournament** (entries due Nov 17): everyone's first version plays everyone else's.
  Weak models are welcome.
- **The final tournament** (entries due Dec 4): decides the rankings and the extra credit.

Details are in [docs/COMPETITION.md](docs/COMPETITION.md#tournaments).

## 4. Quick start

```bash
# 0. Clone the private repository the staff created for you (see docs/COMPETITION.md)
git clone <your-repo-url> && cd <your-repo>

# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e ".[baseline]"

# 2. Get Stockfish (used by some reference bots and to make training labels)
bash scripts/get_stockfish.sh             # then run the export line it prints

# 3. Watch the baseline play the reference bots
python -m fow.arena agents/baseline bot:random bot:greedy bot:guess-sf-4x500 --games 20

# 4. Check that your submission is valid (size, legality, FLOPs, replayability)
python -m fow.validate submission
```

On Sol, run `bash scripts/sol/setup_env.sh` once, then use the job scripts in `scripts/sol/`.
See [docs/RESOURCES.md](docs/RESOURCES.md#sol) for Sol accounts and documentation.

## 5. The starting baseline

`agents/baseline` is a small CNN (314K parameters, no search). It learned by copying the move
full-board Stockfish would play, from 83,000 positions and 12 minutes of CPU training. The
same network is in `submission/`, so you start with a valid entry.

| Player | Rating | What it is |
|---|---:|---|
| `bot:guess-sf-16x1000` | 1225 | Stockfish on 16 guesses of the hidden board, majority vote |
| **`agents/baseline`** | **1217** | the starting network: 4×10⁷ FLOPs per move |
| `bot:guess-sf-4x500` | 1060 | the same idea with 4 guesses |
| `bot:greedy` | 1000 | grabs the most valuable piece it can see (sets the scale) |
| `bot:naive-sf` | 920 | Stockfish pretending the hidden squares are empty |
| `bot:random` | 0 | random legal moves (sets the scale) |

These are local ratings from 600 games, each about ±90.

**There is a lot of room above this.** In a staff test, Stockfish allowed to see the whole board
won every one of 160 games against the strongest bots here. The best fair Fog-of-War play is
far above this table, and the baseline is meant to be beaten. How it was made, and what it
leaves on the table, is in [baselines/imitation/README.md](baselines/imitation/README.md).

## 6. Learn the game

- **Dark chess** on Wikipedia: history and rules: <https://en.wikipedia.org/wiki/Dark_chess>
- **Chess.com Fog of War guide.** It is Chess.com's most popular variant, and you can play it
  there: <https://www.chess.com/terms/fog-of-war-chess>
- **Fog of War on pychess.org**, a free chess-variants site:
  <https://www.pychess.org/variants/fogofwar>
- **The Chess Variant Pages:** <https://www.chessvariants.org/other.dir/fog_of_war_chess.html>
- **Research on strong play:**
  - Zhang & Sandholm (2025), *superhuman Fog-of-War chess* (Obscuro): <https://arxiv.org/abs/2506.01242>
  - Ruoss et al. (2024), *Grandmaster-Level Chess Without Search*, on what a network can learn
    from Stockfish without search: <https://arxiv.org/abs/2402.04494>

Online sites differ from our rules in small ways (for example castling and draws). For this
project, [docs/RULES.md](docs/RULES.md) and `fow/game.py` decide.

## 7. Resources

- **AI coding tools:** ASU gives every student free tools: ChatGPT Edu with Codex, CreateAI,
  and GitHub Copilot Student. See [docs/RESOURCES.md](docs/RESOURCES.md#ai-assistants).
- **Compute:** your Sol class account. See [docs/RESOURCES.md](docs/RESOURCES.md#sol).
- **Libraries:** [python-chess](https://python-chess.readthedocs.io), [PyTorch](https://pytorch.org/docs/),
  [Stockfish](https://stockfishchess.org).

## 8. What is in this repository

| Path | What it is |
|---|---|
| `submission/` | **your agent**; starts as a copy of the baseline |
| `REPRODUCE.md`, `reproduce.sh` | how to rebuild your entry from scratch; the staff run these to replicate it |
| `JOURNAL.md`, `AI_USE.md` | your project journal and AI disclosure; keep them current |
| [`docs/`](docs) | [rules](docs/RULES.md), [agent API](docs/API.md), [submissions and tournaments](docs/COMPETITION.md), [policies](docs/POLICIES.md), [grading](docs/GRADING.md), [resources](docs/RESOURCES.md) |
| `fow/` | rules engine, referee, reference bots, and the tools `arena`, `validate`, `params` |
| `agents/template/` | the smallest valid agent (random moves): the interface in 20 lines |
| `agents/baseline/` | the starting baseline |
| `baselines/imitation/` | the scripts that made the baseline: data generation and training |
| `scripts/` | Stockfish download and Sol job scripts |
| `tests/` | rule tests: `python -m pytest tests` |

## 9. Key dates

| Date | What |
|---|---|
| Fri Oct 23, 11:59 PM | proposal ([what to submit](docs/GRADING.md#proposal-2-points)) |
| Tue Nov 17, 11:59 PM | pre-tournament entry: your first version, any strength |
| the following days | pre-tournament: all entries play each other; you get your results and games |
| Fri Dec 4, 11:59 PM | final entry (model freeze) |
| Dec 5–8 | final tournament |
| Sat Dec 12, 11:59 PM | final report and recorded presentation |

## Questions

Ask on Canvas. Found a bug in the rules engine or referee? Open an issue in this repository with
a game seed that reproduces it.
