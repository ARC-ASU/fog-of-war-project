#!/usr/bin/env bash
# One-time setup on Sol. Run from the repository root on a login node:
#     bash scripts/sol/setup_env.sh
# Module names follow ASU Research Computing's documentation; check it if a module is missing.
set -euo pipefail
module load mamba/latest
mamba create -y -n fow python=3.11
source activate fow
pip install -e ".[baseline]"
bash scripts/get_stockfish.sh
echo "Done. In new shells:  module load mamba/latest && source activate fow && export STOCKFISH=<path printed above>"
