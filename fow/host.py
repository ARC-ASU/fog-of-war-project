"""Runs one submitted agent in its own process and talks to the referee over stdin/stdout.

    python -m fow.host AGENT_DIR [--device cuda:0]

Protocol: one JSON object per line.
    referee -> agent: {"cmd": "reset", "color": "white", "seed": 123}
                      {"cmd": "act", "obs": {...}}
                      {"cmd": "quit"}
    agent -> referee: {"ready": true, "load_seconds": 1.2}   (once, after loading)
                      {"ok": true}                            (after reset)
                      {"move": "e2e4"}                        (after act)
                      {"error": "..."}                        (on an exception)
Anything the agent prints goes to stderr, so it cannot corrupt the protocol.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
import traceback


def load_agent(agent_dir: str, device: str):
    agent_dir = os.path.abspath(agent_dir)
    sys.path.insert(0, agent_dir)
    spec = importlib.util.spec_from_file_location("submitted_agent", os.path.join(agent_dir, "agent.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Agent(agent_dir, device)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_dir")
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    proto = os.fdopen(os.dup(1), "w", buffering=1)   # private copy of stdout for the protocol
    os.dup2(2, 1)                                   # the agent's prints go to stderr
    sys.stdout = sys.stderr

    def send(obj):
        proto.write(json.dumps(obj) + "\n")
        proto.flush()

    t = time.perf_counter()
    try:
        agent = load_agent(args.agent_dir, args.device)
    except Exception:
        send({"error": "load failed: " + traceback.format_exc(limit=5)})
        return
    send({"ready": True, "load_seconds": time.perf_counter() - t})

    for line in sys.stdin:
        msg = json.loads(line)
        try:
            if msg["cmd"] == "reset":
                agent.reset(msg["color"], int(msg["seed"]))
                send({"ok": True})
            elif msg["cmd"] == "act":
                send({"move": str(agent.act(msg["obs"]))})
            elif msg["cmd"] == "quit":
                break
        except Exception:
            send({"error": traceback.format_exc(limit=5)})


if __name__ == "__main__":
    main()
