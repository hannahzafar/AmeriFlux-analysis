#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=02:00:00

module load anaconda
cd $HOME
conda activate micasa

cd $NOBACKUP/ghgc/micasa/AmeriFlux-analysis
./data-extract.py US-Bar

conda deactivate
