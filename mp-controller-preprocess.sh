#!/usr/bin/env bash
# Interactive bash parallel preprocessing (running one subbatch per run)

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <subbatch number>"
    exit 1
fi

module purge
module load python/GEOSpyD/Min24.4.0-0_py3.12


$NOBACKUP/ghgc/micasa/AmeriFlux-analysis/mp-controller-preprocessing.py $1
