"""Check an agent directory the way the ladder will before it plays any rated game.

    python -m fow.validate submission [--device cuda] [--games 10]

Checks
  1. Layout: agent.py and MODEL.md exist; weights are .safetensors only; everything that is
     not a weight file adds up to at most 5 MB.
  2. Size: the parameter count (all tensors in all .safetensors files) is under 250M.
  3. Play: it loads, plays legal moves without errors in games against bot:random as both
     colors, and no move uses more than the per-move FLOP budget.
  4. Replay: with the same seeds it plays exactly the same moves again.
  5. Compute: FLOPs per move (the limit that counts; the same on any machine) and, for
     information, load and move times on this machine.
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys

from .limits import MAX_MOVE_FLOPS, MAX_OTHER_BYTES, MAX_PARAMS
from .params import count_params
from .referee import TimeControl, make_player, play_game

FORBIDDEN_EXT = (".pt", ".pth", ".bin", ".ckpt", ".pkl", ".pickle", ".npy", ".npz", ".onnx", ".h5", ".joblib", ".gguf")
SKIP_DIRS = {"__pycache__", ".git"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_dir")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--games", type=int, default=10)
    args = ap.parse_args(argv)
    d = args.agent_dir
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        print("  FAIL  " + msg)

    print("1. Layout")
    for f in ("agent.py", "MODEL.md"):
        if not os.path.isfile(os.path.join(d, f)):
            fail(f"missing {f}")
    other = 0
    for root, dirs, names in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in names:
            p = os.path.join(root, n)
            if n.endswith(".safetensors"):
                continue
            if n.lower().endswith(FORBIDDEN_EXT):
                fail(f"{os.path.relpath(p, d)}: weights and data must be .safetensors")
            other += os.path.getsize(p)
    print(f"  non-weight files: {other / 1024:.0f} KB (limit {MAX_OTHER_BYTES // 1024} KB)")
    if other > MAX_OTHER_BYTES:
        fail("non-weight files exceed 5 MB")

    print("2. Size")
    total, files = count_params(d)
    for name, n in files:
        print(f"  {n:>14,}  {name}")
    print(f"  {total:>14,}  parameters in total (limit {MAX_PARAMS:,})")
    if total > MAX_PARAMS:
        fail("too many parameters")
    if ok is False:
        print("\nNOT VALID")
        return 1

    print("3. Play")
    try:
        agent = make_player(d, args.device, log_dir="validate_logs")
    except Exception as e:
        fail(f"could not start the agent: {e} (see validate_logs/)")
        print("\nNOT VALID")
        return 1
    print(f"  loaded in {agent.load_seconds:.1f} s")
    bot = make_player("bot:random")
    records = []
    for g in range(args.games):
        w, b = (agent, bot) if g % 2 == 0 else (bot, agent)
        records.append(play_game(w, b, seed=1000 + g, tc=TimeControl(max_flops=MAX_MOVE_FLOPS)))
    for r in records:
        if any(k in r.termination for k in ("error", "illegal", "FLOP")):
            fail(f"game {r.seed}: {r.termination}")
    wins = sum(1 for r in records if (r.result == "1-0") == (r.white == agent.name) and r.result != "1/2-1/2")
    print(f"  {len(records)} games against bot:random: {wins} wins")

    print("4. Replay")
    for r in records[:2]:
        w, b = (agent, bot) if r.white == agent.name else (bot, agent)
        again = play_game(w, b, seed=r.seed, tc=TimeControl(max_flops=MAX_MOVE_FLOPS))
        if again.moves != r.moves:
            fail(f"game {r.seed} went differently on replay: make your agent deterministic given the seed")
    if ok:
        print("  same moves on replay")

    print("5. Compute")
    mine = [(r, side) for r in records for side in ("white", "black")
            if (r.white if side == "white" else r.black) == agent.name]
    flops = sorted(f for r, side in mine for f in r.flops[side])
    if flops:
        print(f"  FLOPs per move: mean {statistics.mean(flops):.3g}, max {flops[-1]:.3g} "
              f"(budget {MAX_MOVE_FLOPS:.3g}, max uses {flops[-1] / MAX_MOVE_FLOPS:.1%} of it)")
        if total > 0 and flops[-1] == 0:
            fail("your agent has parameters but no PyTorch FLOPs were counted: run your networks "
                 "with PyTorch in the thread that calls act() (see docs/COMPETITION.md)")
    times = sorted(t for r, side in mine for t in r.seconds[side])
    if times:
        print("  time on this machine (for information; the ladder limits FLOPs, not time):")
        print(f"  per move: mean {statistics.mean(times) * 1000:.1f} ms, "
              f"95th percentile {times[int(0.95 * (len(times) - 1))] * 1000:.1f} ms, max {times[-1] * 1000:.1f} ms")
    agent.close()
    print("\nVALID" if ok else "\nNOT VALID")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
