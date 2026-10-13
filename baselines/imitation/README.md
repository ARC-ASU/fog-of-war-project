# How the baseline was made

The baseline imitates **full-board Stockfish**, a teacher that sees what your agent cannot.

1. **Data:** `generate_data.py` plays games between reference bots. At about half of the
   positions it records what the side to move can see (plus its memory of enemy pieces) and the
   move Stockfish picks on the true board (5,000 nodes).
2. **Training:** `train.py` fits `agents/baseline/model.py` with cross-entropy over legal moves
   and writes `config.json` and `weights/model.safetensors` into the agent directory.

```bash
export STOCKFISH=/path/to/stockfish
python baselines/imitation/generate_data.py --games 4000 --workers 2 --out data/imitation
python baselines/imitation/train.py --data data/imitation --agent-dir submission --epochs 8
python -m fow.validate submission
```

The shipped baseline used exactly these settings: 4,000 games, about 83,000 positions, 8 epochs.
It took about 30 minutes for the data and 12 minutes for training on 2 CPU cores. A Sol GPU node
does this much faster, and with far more data.

Things this baseline does not do, any of which is a reasonable first project direction:

- **Data and scale:** it trains on very little data with a tiny model.
- **Teacher:** it copies a teacher that can see everything, so it learns moves that only make
  sense with full information.
- **Memory:** its memory is a hand-made "last seen here" map, not learned.
- **Search:** it plays its top move, with no search over its own model.
- **Self-play:** it never plays against itself.
