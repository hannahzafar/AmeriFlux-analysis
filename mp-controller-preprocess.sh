#!/usr/bin/env bash
# Preprocess single site via parallel processing on a compute node
# Arg1 = 1-5 groups in list

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py 5
