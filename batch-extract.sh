#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=02:00:00

module purge
module load anaconda
conda activate micasa

$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/data-extract.py US-Ne1 HH

conda deactivate
