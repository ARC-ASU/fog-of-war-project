#!/bin/bash
# CPU job: play games between reference bots and label positions with full-board Stockfish.
#SBATCH -J fow-data
#SBATCH -q class
#SBATCH -p general            # partition and QoS names: see ASU Research Computing docs
#SBATCH -c 32
#SBATCH --mem=32G
#SBATCH -t 04:00:00
#SBATCH -o runs/%x-%j.out
module load mamba/latest
source activate fow
export STOCKFISH=${STOCKFISH:?set STOCKFISH to your Stockfish binary}
python baselines/imitation/generate_data.py --games 20000 --workers 32 --out data/imitation --seed ${SEED:-0}
