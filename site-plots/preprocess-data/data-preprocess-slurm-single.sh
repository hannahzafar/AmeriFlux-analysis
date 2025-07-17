#!/usr/bin/env bash
#SBATCH --account=s1460
#SBATCH --time=1:30:00
# Preprocess a single site on compute node with pixi

module purge
cd $NOBACKUP/hzafar/ghgc/micasa/fluxnet-model-comparison/site-plots/preprocess-data
pixi shell

$NOBACKUP/hzafar/ghgc/micasa/fluxnet-model-comparison/site-plots/preprocess-data AR-TF1 
