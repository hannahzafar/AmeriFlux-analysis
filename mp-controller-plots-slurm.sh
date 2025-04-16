#!/usr/bin/env bash
#SBATCH --job-name=mp_plotting_slurm
#SBATCH --output=slurm-%j.out      # Capture both stdout and stderr
#SBATCH --error=slurm-%j.out       # Same log file for errors
#SBATCH --account=s1460
#SBATCH --time=1:00:00
#SBATCH --begin=2025-04-15T22:00:00

# Multiprocessing of plot generation on compute node
# Arg1 = 1-5 groups in list

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 1
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 2
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 3
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 4
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 5
