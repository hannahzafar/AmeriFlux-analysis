#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=1:30:00
# Preprocess a single site on compute node

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12

$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/data-preprocessing.py US-RGB DD NPP

module purge
