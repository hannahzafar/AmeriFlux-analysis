#!/usr/bin/env bash
module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 1
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 2
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 3
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 4
$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-plots.py 5
