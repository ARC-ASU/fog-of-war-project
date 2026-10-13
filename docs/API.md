# Agent API (version 1.0)

This is the exact contract between your agent and the referee. Every official game runs through
it, and `python -m fow.validate` checks it. The types are also in [`fow/api.py`](../fow/api.py).

## 1. Files

Your agent is the directory `submission/`. It must contain:

| File | Required | Content |
|---|---|---|
| `agent.py` | yes | defines the class `Agent` (section 2) |
| `MODEL.md` | yes | your model card: parameters, weight files with SHA-256, data, compute, how to reproduce |
| `*.safetensors` | if you have networks | every network weight your agent loads, anywhere inside `submission/` |
| other code and config files | optional | at most 5 MB in total; no other weight or data formats (`.pt`, `.bin`, `.npy`, `.pkl`, ...) |

## 2. The `Agent` class

```python
class Agent:
    def __init__(self, agent_dir: str, device: str) -> None: ...
    def reset(self, color: str, seed: int) -> None: ...
    def act(self, obs: dict) -> str: ...
```

| Method | Called | Arguments | Must |
|---|---|---|---|
| `__init__` | once, when your process starts | `agent_dir`: absolute path of your `submission/` directory; `device`: a PyTorch device string, `"cuda"` on the tournament machine or `"cpu"` | load everything you need; finish within 300 s |
| `reset` | before every game | `color`: `"white"` or `"black"`; `seed`: an integer, different for every game | clear all per-game state; set up your random generator from `seed` |
| `act` | every time it is your move | `obs`: the observation (section 3) | return one string from `obs["legal_moves"]`, within the FLOP budget |

**The lifecycle:**
- One process plays many games in a row: `__init__` once, then `reset`, then `act`, `act`, ...,
  then `reset` for the next game, and so on.
- The referee may also restart your process at any time, so never rely on anything surviving
  between games.

**If something goes wrong:** you lose that game if `act` raises an exception, returns anything
not in `obs["legal_moves"]`, uses more than the FLOP budget, takes longer than the 10 s wall-clock
guard, or your process crashes. If `__init__` fails, you lose every game of that run.

## 3. The observation

`obs` is a plain `dict` decoded from JSON. It holds **only** what you are allowed to know.

| Field | Type | Meaning |
|---|---|---|
| `api_version` | `str` | `"1.0"` |
| `variant` | `str` | `"fow"` (Fog-of-War chess; the field exists so the API can grow) |
| `color` | `str` | your color, `"white"` or `"black"` (it is always your move) |
| `ply` | `int` | half-moves played so far in this game: 0 for White's first move, 1 for Black's first move |
| `own` | `dict[str, str]` | every one of your pieces: square → piece letter |
| `enemy` | `dict[str, str]` | enemy pieces on squares you can see now: square → piece letter |
| `visible` | `list[str]` | every square you can see now, sorted alphabetically; includes your own squares |
| `legal_moves` | `list[str]` | your legal moves in UCI notation; never empty |
| `castling` | `{"kingside": bool, "queenside": bool}` | your remaining castling rights |
| `last_move` | `str` or `null` | the move you played on your previous turn (`null` on your first move) |
| `lost_on` | `str` or `null` | the square where the opponent captured one of your pieces on their last move, else `null` |

**Formats:**
- **Squares** are lowercase file + rank: `"a1"` … `"h8"`. White starts on ranks 1–2, and the
  board is never flipped.
- **Pieces** are uppercase letters for both colors: `P` pawn, `N` knight, `B` bishop, `R` rook,
  `Q` queen, `K` king. Which side a piece is on is given by the field it is in (`own` or `enemy`).
- **Moves** are UCI: from-square + to-square, plus a promotion letter (`q r b n`) when a pawn
  promotes, for example `"e2e4"`, `"g1f3"`, `"e7e8q"`. Castling is the king's move: `"e1g1"`,
  `"e1c1"`, `"e8g8"`, `"e8c8"`. An en-passant capture is the pawn's diagonal move.

**Example** (Black's first move after `1. e4`; lists shortened):

```json
{
  "api_version": "1.0",
  "variant": "fow",
  "color": "black",
  "ply": 1,
  "own": {"a8": "R", "b8": "N", "c8": "B", "d8": "Q", "e8": "K", "a7": "P", "...": "..."},
  "enemy": {},
  "visible": ["a5", "a6", "a7", "a8", "b5", "...", "h8"],
  "legal_moves": ["g8h6", "g8f6", "b8c6", "b8a6", "h7h6", "...", "a7a5"],
  "castling": {"kingside": true, "queenside": true},
  "last_move": null,
  "lost_on": null
}
```

What you see follows the game rules ([RULES.md](RULES.md)): your pieces, the squares your legal
moves land on, enemy pieces on those squares, and the pawn an en-passant capture would remove.
You are never told the opponent's moves or who the opponent is.

## 4. Compute and time

- **FLOPs:** each `act` call may use at most **10¹² FLOPs**. The referee wraps the call in
  PyTorch's `torch.utils.flop_counter.FlopCounterMode`, which counts matrix multiplications,
  convolutions and attention. Run all network computation with PyTorch, in the thread that
  calls `act`. Details: [COMPETITION.md](COMPETITION.md#how-compute-is-counted).
- **Wall clock:** 300 s for `__init__`, 10 s for any `act`. These only catch agents that hang.
- **Output:** anything you print goes to a log file. The referee never reads it.

## 5. The runtime

Official games run on a Linux machine with an NVIDIA RTX Pro 6000 GPU.

- **Python and packages:** Python 3.11 with these packages installed: PyTorch, NumPy,
  safetensors, python-chess, and this repository's `fow` package. Exact versions will be
  announced with the runtime image, and you will be able to run the image yourself.
- **Other pure-Python code:** copy it into `submission/` (within the 5 MB limit).
- **Compiled extensions:** ask on Canvas first.
- **No network access.** Read files only inside `submission/`, and don't write files.
- **Replayable:** given the same `seed` and the same observations, your agent must return the
  same moves. Use only `seed` for randomness, and on the GPU set
  `torch.backends.cudnn.deterministic = True` (or avoid nondeterministic operations).

## 6. Under the hood

You don't need this to write an agent, but it is what the referee does.

Your agent runs as `python -m fow.host submission --device cuda`. It talks to the referee with
one JSON object per line on stdin and stdout:

```
referee -> agent   {"cmd": "reset", "color": "white", "seed": 123}
                   {"cmd": "act", "obs": {...}}
                   {"cmd": "quit"}
agent -> referee   {"ready": true, "load_seconds": 1.2}       once, after __init__
                   {"ok": true}                                after reset
                   {"move": "e2e4", "flops": 39900000}         after act
                   {"error": "..."}                            if your code raised
```

`python -m fow.validate submission` exercises all of the above before you submit.

## 7. Changes

This API is version 1.0. Any change will be announced on Canvas, with the new `api_version`.
