"""Count model parameters the way the ladder does: every tensor element stored in every
*.safetensors file inside the agent directory (read from the file headers, no framework needed)."""
from __future__ import annotations

import json
import os
import struct
import sys
from math import prod


def safetensors_params(path: str) -> int:
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
    return sum(prod(v["shape"]) for k, v in header.items() if k != "__metadata__")


def count_params(agent_dir: str) -> tuple[int, list[tuple[str, int]]]:
    files = []
    for root, _, names in os.walk(agent_dir):
        for name in names:
            if name.endswith(".safetensors"):
                p = os.path.join(root, name)
                files.append((os.path.relpath(p, agent_dir), safetensors_params(p)))
    return sum(n for _, n in files), sorted(files)


if __name__ == "__main__":
    total, files = count_params(sys.argv[1])
    for name, n in files:
        print(f"{n:>14,}  {name}")
    print(f"{total:>14,}  total")
