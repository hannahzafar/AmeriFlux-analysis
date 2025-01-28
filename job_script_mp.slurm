#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=1:00:00

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12

$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp_controller.py
