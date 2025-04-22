#!/usr/bin/env python
# Script to control multiprocessing for data-preprocessing.py

import numpy as np
import pandas as pd
import subprocess
import multiprocessing
import argparse
import sys
import os

# Import list of all sites
amer_filepath = 'ameriflux-data/'
meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only
fluxnet_list = fluxnet_meta['Site ID'].to_list()

# Testing
# fluxnet_list = ['US-A32', 'AR-TF1']
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
    with multiprocessing.Pool() as pool: # should be fine to not specify pool size as long as no mem issues
        results = pool.map(run_script, arg_list) # Use map to run `run_script` across the arg_list
    
    return results

# Run the script in parallel (interactive safe)
if __name__ == "__main__":
    results = run_in_parallel(fluxnet_list)
    #print(results)
