# Submissions, limits and ratings

## Your repository

1. Create your own repository from this template ("Use this template" on GitHub). Make it
   **private** and add the course staff as collaborators (usernames will be announced on Canvas).
2. Keep your agent in [`submission/`](../submission). It starts as a copy of the baseline, so a
   valid entry exists from day one.
3. Keep your notes in [`JOURNAL.md`](../JOURNAL.md) and your AI disclosure in
   [`AI_USE.md`](../AI_USE.md) (see [POLICIES.md](POLICIES.md)).

## The agent interface

`submission/agent.py` must define a class `Agent`:

```python
class Agent:
    def __init__(self, agent_dir: str, device: str): ...   # load your model; device is e.g. "cuda" or "cpu"
    def reset(self, color: str, seed: int) -> None: ...    # a new game starts; color is "white" or "black"
    def act(self, obs: dict) -> str: ...                    # return one move from obs["legal_moves"]
```

Everything between the observation and the move is yours to design: memory, belief tracking,
search with your own model, sampling. [POLICIES.md](POLICIES.md) lists what may run at play time.

### The observation

```json
{
  "color": "black",
  "ply": 1,
  "own":     {"e8": "K", "d8": "Q", "e7": "P", "...": "..."},
  "enemy":   {},
  "visible": ["a5", "a6", "a7", "...", "h8"],
  "legal_moves": ["g8h6", "g8f6", "b8c6", "b8a6", "h7h6", "...", "a7a5"],
  "castling": {"kingside": true, "queenside": true},
  "last_move": null,
  "lost_on": null
}
```

| Field | Meaning |
|---|---|
| `color` | your color |
| `ply` | half-moves played so far in this game |
| `own` | your pieces: square to letter (`P N B R Q K`) |
| `enemy` | enemy pieces on squares you can see now |
| `visible` | every square you can see now |
| `legal_moves` | your legal moves in UCI notation (`e2e4`, `e7e8q`, castling as `e1g1`) |
| `castling` | your remaining castling rights |
| `last_move` | the move you played last (null at the start) |
| `lost_on` | the square where the opponent captured one of your pieces on their last move, or null |

You get no other information. In particular you are never told who your opponent is.

### How the referee runs your agent

- Your agent runs in its own process (`python -m fow.host submission --device cuda`) and talks
  to the referee over a pipe. Anything you print goes to a log, not to the referee.
- The same process plays many games in a row. `reset` is called before each game. **Do not
  carry information from one game to the next.**
- **Replayable play:** given the same seed and the same observations, your agent must play the
  same moves. Use only the seed passed to `reset` for randomness, and turn on deterministic
  GPU settings if you use a GPU.
- Your agent may read files only inside its own directory and may not use the network.

## Limits

| Limit | Value |
|---|---|
| Core models | one or more **neural networks**, fewer than **250M parameters** in total (see below) |
| Weight files | `.safetensors` only; every tensor in them counts as parameters |
| Everything else in `submission/` (code, configs) | at most 5 MB |
| Compute per move | at most **10¹² FLOPs** (1 TFLOP) per call to `act`, counted as described below |
| Wall clock | 10 s per move and 300 s to load, only to catch agents that hang; the ladder runs on an NVIDIA RTX Pro 6000 |
| GPU memory | announced before the first ladder run |

### Core models

Your agent's judgment must come from neural networks you trained or fine-tuned.

- **Several networks are allowed:** for example a policy network, a value network and a belief
  network, or an ensemble. Their parameter counts add up, and the total must stay under 250M.
- **Every network you use at play time must be in your submission.** Its weights go in
  `.safetensors` files inside `submission/`, loaded by your agent and counted as parameters.
- **No other learned or stored knowledge at play time:** no decision trees, nearest-neighbour
  lookups, position or move tables, or statistics gathered from games.
- **Plain code may handle the rest:** the game rules, encoding the observation, memory of what
  you have seen, sampling, and search that calls your networks. See
  [POLICIES.md](POLICIES.md).

**Parameters** are counted from your weight files by `python -m fow.params submission`: every
element of every tensor in every `.safetensors` file, including buffers such as batch-norm
statistics. Storing weights in fewer bits does not lower the count, and neither does a network
being used several times.

### How compute is counted

The budget is in FLOPs rather than seconds, so you can check it on any machine, CPU included,
and get the same number the ladder gets.

- **What is counted:** the referee wraps every call to `act` in PyTorch's
  `torch.utils.flop_counter.FlopCounterMode`. It counts the matrix multiplications,
  convolutions and attention your networks run during that call, across all forward passes:
  search, sampling and ensembles included.
- **For scale:** one forward pass of a network with P parameters over T input tokens costs
  roughly 2·P·T FLOPs. At the 250M limit with a 64-token board, that is about 3×10¹⁰, so the
  budget allows roughly 30 such passes per move. The baseline uses 4×10⁷.
- **What you must do so it is counted:** run your networks with PyTorch, in the thread that
  calls `act`. Network computation done any other way (NumPy, other frameworks, custom
  kernels, other threads or processes) is not allowed at play time.
- **What happens if you go over:** a move over the budget loses the game. `fow.validate`
  reports your FLOPs per move, and `python -m fow.arena ... --official` applies the ladder's
  limits.

Before you tag an entry, run:

```bash
python -m fow.validate submission --device cuda
```

It checks the layout, counts parameters, plays games against `bot:random` with the FLOP budget
enforced, replays two of them to check that your moves are reproducible, and reports FLOPs per
move (plus load and move times on your machine, for information).

## Entering the ladder

1. Make sure `python -m fow.validate submission` says **VALID**.
2. Fill in `submission/MODEL.md`: parameter count, weight files with SHA-256 checksums, data,
   compute, and how to reproduce the weights.
3. Create a GitHub release in your repository whose tag starts with `ladder-`
   (for example `ladder-2026-11-06`).
   - Weight files under 100 MB can be committed.
   - Larger weight files go in the release as assets (up to 2 GB each), placed where
     `agent.py` expects them inside `submission/`.
4. Each ladder run uses your most recent `ladder-` release created before its cutoff.

## Ratings

- Ratings are Elo, fitted with a Bradley–Terry model to all ladder games. A draw counts as half
  a win for each side.
- The reference bots keep fixed ratings, so the scale stays the same from week to week.
  The scale is set by `bot:random` = 0 and `bot:greedy` = 1000.
- Every week each entry plays both colors against the reference bots and against entries of
  similar strength.
- The leaderboard shows each rating with its 95% interval and your parameter count.
- `python -m fow.arena` gives you the same kind of estimate locally.

### Size-adjusted rating

Smaller models are preferred. Your rank uses the size-adjusted rating:

```
adjusted Elo = Elo + β · log2( 250M / max(P, 1M) )
```

where P is your parameter count:

- **β:** the Elo bonus for halving your model's size. It will be calibrated on staff baselines
  trained at several sizes, announced before the first ladder run, and then not changed.
- **The 1M floor:** models below 1M parameters get the 1M bonus.

### Schedule

| Date | Event |
|---|---|
| Fri Oct 30, 11:59 PM | proposal due |
| weekly from early November | ladder runs (dates and cutoffs on Canvas) |
| Tue Nov 17, 11:59 PM | checkpoint due |
| Fri Dec 4, 11:59 PM | **model freeze**: your last `ladder-` release before this counts for the final tournament |
| Dec 5–8 | final tournament (many more games per entry) |
| Sat Dec 12, 11:59 PM | final report and recorded presentation due |

## Reference bots

| Name | What it does |
|---|---|
| `bot:random` | uniform over legal moves |
| `bot:greedy` | takes the most valuable visible piece; avoids squares it can see are attacked |
| `bot:naive-sf` | Stockfish on a board with only the pieces it can see |
| `bot:guess-sf-KxN` | samples K full boards consistent with what it has seen, runs Stockfish for N nodes on each, plays the most-voted move |

Their provisional ratings are in [`fow/bots.py`](../fow/bots.py) and will be re-measured on
the ladder. They are weak: none of them reasons about what the opponent can see, and a network
trained for minutes reaches their level. Most of the ladder will be above them.
