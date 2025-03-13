#!/usr/bin/env python
# Script to control multiprocessing and looping for plots-generator.py

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

# Fluxnet_list is 196 items, split into sublists for multiple smaller sbatch runs
# Function to split list into semi-equal sized n-number of groups
def split_into_groups(list, n):
    k, m = divmod(len(list), n)
    return [list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

#Run 5 batch jobs that loop through fluxnet_list
fluxnet_groups = split_into_groups(fluxnet_list,5)

# Pick the one we want via sbatch input
fluxnet_sel = fluxnet_groups[subbatch-1]

# Function to run script within script
def run_script(arg_item): 
    script = "plots-generator.py"
    # Convert argument to string if it's not already
    arg_str = str(arg_item)
    cmd = ["python", script, arg_str]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Return stdout only if it's not empty, otherwise return stderr if it exists
    if result.stdout.strip():
        return result.stdout.strip()
    elif result.returncode != 0:
        return f"Error with {arg_str}: {result.stderr.strip()}"
    else:
        return None  # Return None for successful runs with no output

# Function to run scripts in parallel using Pool
def run_in_parallel(arg_list):
    # Define the pool size (number of processes)
    pool_size = multiprocessing.cpu_count() 
    with multiprocessing.Pool(pool_size) as pool:
        # Use map to run `run_script` across the arg_list
        all_results = pool.map(run_script, arg_list)

    # Filter out None values more explicitly
    results = [r for r in all_results if r is not None and r != "None"]
    return results


# Run the script in parallel
results = run_in_parallel(fluxnet_sel)

# Print only if there are actual results
if results:
    print("Issues found during execution:")
    for result in results:
        print(result)

else:
    print("All processes completed successfully with no issues.")