#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=1:30:00

# Arg1 = 1-5 groups in list

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 1
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 2
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 3
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 4
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 5
