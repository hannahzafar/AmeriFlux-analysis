#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=00:30:00

module load anaconda
cd $HOME
conda activate micasa

cd $NOBACKUP/ghgc/micasa/AmeriFlux-analysis
./data-extract.py US-SRC

conda deactivate
