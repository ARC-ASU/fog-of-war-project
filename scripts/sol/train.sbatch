#!/bin/bash
# GPU job: train the imitation policy into submission/.
#SBATCH -J fow-train
#SBATCH -q class
#SBATCH -p general            # partition and QoS names: see ASU Research Computing docs
#SBATCH -G 1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 04:00:00
#SBATCH -o runs/%x-%j.out
module load mamba/latest
source activate fow
python baselines/imitation/train.py --data data/imitation --agent-dir submission --epochs 10 --device cuda
python -m fow.validate submission --device cuda
