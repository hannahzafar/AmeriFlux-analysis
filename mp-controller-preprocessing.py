#!/usr/bin/env python
# Script to control multiprocessing for data-preprocessing.py

import numpy as np
import pandas as pd
import subprocess
import multiprocessing
import argparse
import sys

# Parse input args
parser = argparse.ArgumentParser(description='Subbatch number')
parser.add_argument('subbatch', type=int)
args = parser.parse_args()
subbatch = args.subbatch

# Import list of all sites
amer_filepath = 'ameriflux-data/'
meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only
fluxnet_list = fluxnet_meta['Site ID'].to_list()

# Testing
# fluxnet_list = ['US-A32', 'AR-TF1']

# Fluxnet_list is 196 items, split into sublists for multiple smaller sbatch runs
# Function to split list into semi-equal sized n-number of groups
def split_into_groups(list, n):
    k, m = divmod(len(list), n)
    return [list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

# Let's do 5 batch jobs that loop through fluxnet_list
fluxnet_groups = split_into_groups(fluxnet_list,5)

# Pick the one we want via sbatch input
fluxnet_sel = fluxnet_groups[subbatch-1]

# Function to run script within script
def run_script(arg_list): 
    script = "data-preprocessing.py"
    cmd = ["python", script, arg_list]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True) # check=True will crash if error
        print(result.stdout.strip())
        return result.stdout.strip() 
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return f"FAILED: {arg_list}"

# Function to run scripts in parallel using Pool
def run_in_parallel(arg_list):
    # Define the pool size (number of processes)
    pool_size = multiprocessing.cpu_count()  # Or specify a custom number like 4
    with multiprocessing.Pool(pool_size) as pool:
        # Use map to run `run_script` across the arg_list
        results = pool.map(run_script, arg_list)
    
    return results


# Run the script in parallel (interactive safe)
if __name__ == "__main__":
    results = run_in_parallel(fluxnet_sel)
    #print(results)
