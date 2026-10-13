#!/usr/bin/env bash
# Reproduce submission/ end to end, from a fresh clone. The staff run this file to replicate
# your entry (docs/POLICIES.md), so keep it working and keep REPRODUCE.md in sync with it.
#
# As shipped, it reproduces the baseline: about 30 minutes of data generation on 2 CPU cores
# and about 12 minutes of training on CPU (much faster with more cores and a GPU).
#
#   bash reproduce.sh                 # uses $STOCKFISH, $WORKERS (default 2), $DEVICE (cpu or cuda)
set -euo pipefail
WORKERS=${WORKERS:-2}
DEVICE=${DEVICE:-$(python -c "import torch; print('cuda' if torch.cuda.is_available() else 'cpu')")}
: "${STOCKFISH:?set STOCKFISH to your Stockfish binary (bash scripts/get_stockfish.sh)}"

echo "== 1. data: 4,000 games between reference bots, labelled by full-board Stockfish"
python baselines/imitation/generate_data.py --games 4000 --workers "$WORKERS" --out data/imitation --seed 0

echo "== 2. training: 8 epochs into submission/"
python baselines/imitation/train.py --data data/imitation --agent-dir submission --epochs 8 --seed 0 --device "$DEVICE"

echo "== 3. checks"
python -m fow.validate submission --device "$DEVICE"
sha256sum submission/weights/*.safetensors
