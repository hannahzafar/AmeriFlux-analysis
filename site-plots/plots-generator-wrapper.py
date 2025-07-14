#!/usr/bin/env python
# Wrapper script to run plots-generator.py for all the sites in the Fluxnet list 
# (without multiprocessing, not necessary due to performance)

import numpy as np
import pandas as pd
import subprocess
import importlib

# Import workaround for file with dashes in name
mp_controller = importlib.import_module("mp-controller-preprocessing")
#from mp_controller import run_py_script


if __name__ == "__main__":
    # Import/format the list of paths
    amer_filepath = 'ameriflux-data/'
    meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
    ameriflux_meta = pd.read_csv(meta_file, sep='\t')
    fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only
    fluxnet_list = fluxnet_meta['Site ID'].to_list()
    
    script = "plots-generator.py"

    for fluxnet_item in fluxnet_list:
        mp_controller.run_py_script(script, fluxnet_item)
