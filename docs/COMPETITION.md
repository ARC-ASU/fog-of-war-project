# Submissions, limits, tournaments and ratings

## Your repository

1. **Create your private repository** from this template, before the proposal deadline:
   - On this repository's GitHub page, click **Use this template → Create a new repository**,
     choose your own account, and set it to **Private**.
   - In your new repository, go to **Settings → Collaborators** and add **both**
     [@3rdAT](https://github.com/3rdAT) and [@Slash0BZ](https://github.com/Slash0BZ). The staff
     will only read your repository, never push to it.
   - Keep it private: never make it public or share access with other students.
   - Your proposal is this repository's link plus a filled-in [`PLAN.md`](../PLAN.md)
     ([GRADING.md](GRADING.md#proposal-2-points)).
2. **To receive fixes to this template** (rules engine, tools, docs), add it as a second remote
   once, then pull from it when fixes are announced:
   ```bash
   git remote add upstream https://github.com/ARC-ASU/fog-of-war-project.git
   git pull upstream main
   ```
   Official games always use the official `fow` package, whatever your copy contains.
3. **Your agent** lives in [`submission/`](../submission). It starts as a copy of the
   baseline, so a valid entry exists from day one.
4. **Your documentation:** keep [`REPRODUCE.md`](../REPRODUCE.md) and `reproduce.sh` current.
   The staff will rerun your training from scratch
   ([replication](POLICIES.md#documentation-and-end-to-end-replication)).
5. **Your notes:** keep [`JOURNAL.md`](../JOURNAL.md) and your AI disclosure
   [`AI_USE.md`](../AI_USE.md) current.
6. **Commit and push as you work:** one logical step per commit, and pushed commits every week
   ([the commit rules](POLICIES.md#your-repository-and-commit-history)).

## The agent interface

`submission/agent.py` defines a class `Agent` with three methods:

```python
class Agent:
    def __init__(self, agent_dir: str, device: str) -> None: ...   # load your networks
    def reset(self, color: str, seed: int) -> None: ...            # a new game starts
    def act(self, obs: dict) -> str: ...                            # return one of obs["legal_moves"]
```

The observation is a dictionary with what your side can see: your pieces, the enemy pieces on
visible squares, the visible squares, your legal moves, and a few more fields.

**The exact specification is [API.md](API.md):** every field and its type, the move format,
the lifecycle, error handling and the runtime. Everything between the observation and the
move is yours to design: memory, belief tracking, search with your own networks, sampling.
[POLICIES.md](POLICIES.md) lists what may run at play time.

## Limits

| Limit | Value |
|---|---|
| Core models | one or more **neural networks**, fewer than **250M parameters** in total (see below) |
| Weight files | `.safetensors` only; every tensor in them counts as parameters |
| Everything else in `submission/` (code, configs) | at most 5 MB |
| Compute per move | at most **10¹² FLOPs** (1 TFLOP) per call to `act`, counted as described below |
| Wall clock | 10 s per move and 300 s to load, only to catch agents that hang; tournaments run on an NVIDIA RTX Pro 6000 |
| GPU memory | announced before the pre-tournament |

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
and get the same number the tournaments get.

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
  reports your FLOPs per move, and `python -m fow.arena ... --official` applies the
  tournament limits.

Before you submit an entry, run:

```bash
python -m fow.validate submission --device cuda
```

It checks the layout, counts parameters, plays games against `bot:random` with the FLOP budget
enforced, replays two of them to check that your moves are reproducible, and reports FLOPs per
move (plus load and move times on your machine, for information).

## Submitting an entry

1. Make sure `python -m fow.validate submission` says **VALID**.
2. Fill in `submission/MODEL.md`: parameter count, weight files with SHA-256 checksums, data,
   compute, and how to reproduce the weights.
3. Create a GitHub release in your repository whose tag starts with `entry-`
   (for example `entry-1`, `entry-2`, ...).
   - Weight files under 100 MB can be committed.
   - Larger weight files go in the release as assets (up to 2 GB each), placed where
     `agent.py` expects them inside `submission/`.
4. Each tournament uses your most recent `entry-` release created before its deadline.

## Tournaments

| Date | Event |
|---|---|
| Fri Oct 23, 11:59 PM | proposal due |
| **Tue Nov 17, 11:59 PM** | **pre-tournament entry due** |
| the following days | **pre-tournament**: every entry plays every other entry, plus the reference bots |
| **Fri Dec 4, 11:59 PM** | **model freeze**: final entry due |
| Dec 5–8 | **final tournament**, with many more games per entry |
| Sat Dec 12, 11:59 PM | final report and recorded presentation due |

**The pre-tournament** is a first look at the field, not a judgment of your model.
- Every valid entry plays every other entry, with both colors, and the reference bots.
- An early, weak model is perfectly fine. What counts is that it is valid and plays.
- Afterwards you receive the ratings and the records of your own games, to find out where your
  agent loses before the final tournament.

**The final tournament** decides the rankings and the extra credit
([GRADING.md](GRADING.md#extra-credit-top-10-of-the-final-tournament)). Extra practice rounds
may be announced on Canvas if time allows.

## Ratings

- **How ratings are computed:** Elo, fitted with a Bradley–Terry model to all games of a
  tournament. A draw counts as half a win for each side.
- **A fixed scale:** the reference bots keep fixed ratings, so the pre-tournament and the final
  tournament share one scale. It is set by `bot:random` = 0 and `bot:greedy` = 1000.
- **What is published:** each rating with its 95% interval and the entry's parameter count.
- **Locally:** `python -m fow.arena` gives you the same kind of estimate.

### Size-adjusted rating

Smaller models are preferred. Rankings use the size-adjusted rating:

```
adjusted Elo = Elo + β · log2( 250M / max(P, 1M) )
```

where P is your parameter count:

- **β:** the Elo bonus for halving your model's size. It will be calibrated on staff baselines
  trained at several sizes, announced before the pre-tournament, and then not changed.
- **The 1M floor:** models below 1M parameters get the 1M bonus.

## Reference bots

| Name | What it does |
|---|---|
| `bot:random` | uniform over legal moves |
| `bot:greedy` | takes the most valuable visible piece; avoids squares it can see are attacked |
| `bot:naive-sf` | Stockfish on a board with only the pieces it can see |
| `bot:guess-sf-KxN` | samples K full boards consistent with what it has seen, runs Stockfish for N nodes on each, plays the most-voted move |

Their provisional ratings are in [`fow/bots.py`](../fow/bots.py) and will be re-measured in
the tournaments. They are weak: none of them reasons about what the opponent can see, and a
network trained for minutes reaches their level. Expect most entries to end up above them.
