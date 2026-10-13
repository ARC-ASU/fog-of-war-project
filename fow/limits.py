"""The tournament limits in one place (also documented in docs/COMPETITION.md)."""

MAX_PARAMS = 250_000_000          # total parameters in all .safetensors files of a submission
MAX_MOVE_FLOPS = 1_000_000_000_000  # 1e12 PyTorch FLOPs per move, counted while act() runs
MOVE_WALL_SECONDS = 10.0          # wall-clock guard per move, only to catch hangs
LOAD_SECONDS = 300.0              # time allowed to load the agent
MAX_OTHER_BYTES = 5 * 1024 * 1024  # code and config files (everything that is not .safetensors)
