#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=0:30:00
# Multiprocessing of plot generation on compute node (I honestly don't think this is even necessary)
# Arg1 = 1-5 groups in list

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 1
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 2
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 3
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 4
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 5
