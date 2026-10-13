"""The referee: owns the true board, sends each side only its own observation, enforces the clock.

A player is either a path to an agent directory (run in a separate process through fow.host)
or a reference bot name such as "bot:greedy" (run in-process; bots only read observations).

Losing conditions besides having your king captured: an illegal move, an exception, a crash,
or running out of time.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field

from .bots import make_bot
from .game import Game


@dataclass
class TimeControl:
    """Per side: `clock` seconds for the whole game plus `increment` per move, and no single move
    may take longer than `move_cap` seconds. None means unlimited. Official values are announced
    in docs/COMPETITION.md."""
    clock: float | None = None
    increment: float = 0.0
    move_cap: float | None = None
    load_timeout: float = 300.0


class AgentError(Exception):
    pass


class ProcessPlayer:
    """A submitted agent running in its own process."""

    def __init__(self, agent_dir: str, device: str = "cpu", log_path: str | None = None,
                 load_timeout: float = 300.0):
        self.name = os.path.normpath(agent_dir)
        self.agent_dir, self.device, self.log_path, self.load_timeout = agent_dir, device, log_path, load_timeout
        self.proc = None
        self.load_seconds = None
        self._start()

    def _start(self):
        log = open(self.log_path, "a") if self.log_path else subprocess.DEVNULL
        env = dict(os.environ, PYTHONUNBUFFERED="1")
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "fow.host", self.agent_dir, "--device", self.device],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True, bufsize=1, env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.lines: queue.Queue = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        msg = self._get(self.load_timeout)
        if not msg.get("ready"):
            raise AgentError(msg.get("error", "agent failed to start"))
        self.load_seconds = msg["load_seconds"]

    def _reader(self):
        for line in self.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def _get(self, timeout: float | None) -> dict:
        try:
            line = self.lines.get(timeout=timeout)
        except queue.Empty:
            self.kill()
            raise AgentError("timeout")
        if line is None:
            raise AgentError("agent process exited")
        return json.loads(line)

    def _call(self, msg: dict, timeout: float | None) -> dict:
        if self.proc is None or self.proc.poll() is not None:
            self._start()
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        reply = self._get(timeout)
        if "error" in reply:
            raise AgentError(reply["error"])
        return reply

    def reset(self, color: str, seed: int) -> None:
        self._call({"cmd": "reset", "color": color, "seed": seed}, timeout=60)

    def act(self, obs: dict, timeout: float | None) -> str:
        return self._call({"cmd": "act", "obs": obs}, timeout)["move"]

    def kill(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.kill()
        self.proc = None

    def close(self):
        if self.proc is not None and self.proc.poll() is None:
            try:
                self.proc.stdin.write(json.dumps({"cmd": "quit"}) + "\n")
                self.proc.stdin.flush()
                self.proc.wait(timeout=5)
            except Exception:
                self.kill()
        self.proc = None


class BotPlayer:
    def __init__(self, spec: str):
        self.name = spec
        self.bot = make_bot(spec)

    def reset(self, color, seed):
        self.bot.reset(color, seed)

    def act(self, obs, timeout):
        return self.bot.act(obs)

    def close(self):
        self.bot.close()


def make_player(spec: str, device: str = "cpu", log_dir: str | None = None, load_timeout: float = 300.0):
    if spec.startswith("bot:"):
        return BotPlayer(spec)
    log = None
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log = os.path.join(log_dir, os.path.basename(os.path.normpath(spec)) + ".stderr.log")
    return ProcessPlayer(spec, device, log, load_timeout)


@dataclass
class GameRecord:
    white: str
    black: str
    seed: int
    result: str = ""
    termination: str = ""
    plies: int = 0
    moves: list = field(default_factory=list)
    seconds: dict = field(default_factory=dict)   # color -> list of per-move times


def play_game(white, black, seed: int, tc: TimeControl | None = None) -> GameRecord:
    """Play one game between two players (objects from make_player)."""
    tc = tc or TimeControl()
    game = Game()
    players = {"white": white, "black": black}
    rec = GameRecord(white.name, black.name, seed, seconds={"white": [], "black": []})
    clock = {"white": tc.clock, "black": tc.clock}
    for i, color in enumerate(("white", "black")):
        try:
            players[color].reset(color, seed * 2 + i)
        except Exception as e:
            game.forfeit(color, f"reset failed: {e}")
    while not game.over:
        color = game.turn
        limit = tc.move_cap
        if clock[color] is not None:
            limit = clock[color] if limit is None else min(limit, clock[color])
        obs = game.observation()
        t = time.perf_counter()
        try:
            move = players[color].act(obs, None if limit is None else limit + 0.5)
        except AgentError as e:
            last = (str(e).strip().splitlines() or ["error"])[-1]
            game.forfeit(color, f"{color} error: {last[:200]}")
            break
        dt = time.perf_counter() - t
        rec.seconds[color].append(round(dt, 4))
        if tc.move_cap is not None and dt > tc.move_cap:
            game.forfeit(color, f"{color} exceeded the per-move cap ({dt:.2f}s)")
            break
        if clock[color] is not None:
            clock[color] -= dt
            if clock[color] < 0:
                game.forfeit(color, f"{color} ran out of time")
                break
            clock[color] += tc.increment
        try:
            game.play(move)
        except ValueError:
            game.forfeit(color, f"{color} played an illegal move: {move!r}")
            break
    rec.result, rec.termination = game.result, game.termination
    rec.plies, rec.moves = len(game.moves), game.moves
    return rec
