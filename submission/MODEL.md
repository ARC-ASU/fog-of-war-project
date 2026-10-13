# Model card: YOUR AGENT

> This directory starts as a copy of `agents/baseline`. Replace everything below as your agent changes.


- **Name:** imitation baseline (residual CNN, no search)
- **Core model:** `model.py` `PolicyNet(in_planes=22, channels=64, blocks=4)`; scores every (from, to) square pair
- **Parameters:** 314,057 as counted by `python -m fow.params agents/baseline` (312,896 trainable weights plus batch-norm statistics stored in the file)
- **Weight files and SHA-256:** `weights/model.safetensors`, `0a0bab7d26538b29f320e550141b7cce98e3e6729043f7a465ea4b79b8e740d5`
- **Input:** 22 planes; see `features.py`
- **Training data:** about 83,000 positions from 4,000 games between reference bots, each labelled with full-board Stockfish 16 at 5,000 nodes (`baselines/imitation/generate_data.py --games 4000 --workers 2 --seed 0`)
- **Training:** `baselines/imitation/train.py --epochs 8 --seed 0` (AdamW, one-cycle learning rate 2e-3, batch 256)
- **Training compute:** about 12 minutes on 2 CPU cores; no GPU
- **Validation match with teacher:** 39.4% of held-out positions (top move equals the teacher's)
- **How to reproduce:** see `baselines/imitation/README.md`
