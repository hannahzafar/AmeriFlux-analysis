#!/usr/bin/env python
# File to control multiprocessing for the data-preprocessing script

import numpy as np
import pandas as pd
import subprocess
import multiprocessing

# Import list of all sites
# amer_filepath = 'ameriflux-data/'
# meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
# ameriflux_meta = pd.read_csv(meta_file, sep='\t')
# fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only
# fluxnet_list = fluxnet_meta['Site ID'].to_list()

# Testing
fluxnet_list = ['US-A32', 'AR-TF1']

# Define variables 
def run_script(arg_list): 
    script = "data-preprocessing.py"
    cmd = ["python", script, arg_list]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout.strip()
    return out

# print(run_script('US-RGB'))


# Function to run scripts in parallel using Pool
def run_in_parallel(arg_list):
    # Define the pool size (number of processes)
    pool_size = multiprocessing.cpu_count()  # Or specify a custom number like 4
    with multiprocessing.Pool(pool_size) as pool:
        # Use map to run `run_script` across the arg_list
        results = pool.map(run_script, arg_list)
    
    return results


# Run the script in parallel
results = run_in_parallel(fluxnet_list)
print(results)