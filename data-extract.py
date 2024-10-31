#!/usr/bin/env python
# Extract fluxnet and micasa data as csv for plotting
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import glob
import argparse
import sys
import os


######### functions ############
def get_single_match(pattern):
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise ValueError(f"No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

# Input site ID as parse argument
parser = argparse.ArgumentParser(description='User-specified parameters')
parser.add_argument('site_ID', type=str,
                     help='FluxNet/AmeriFLUX Site Identifier (XX-XXX)')
args = parser.parse_args()
site_ID = args.site_ID

# Open site ID metadata and extract lat/lon
filepath = 'ameriflux-data/'
meta_file = filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
site_lat = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Latitude (degrees)'].values
site_lon = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Longitude (degrees)'].values
# print(site_lat, site_lon)

# Open site data and access time indices
site_file = get_single_match(filepath + 'AMF_' + site_ID + 
                            '_FLUXNET_SUBSET_*/AMF_' + site_ID + '_FLUXNET_SUBSET_HH_*.csv')
fluxnet_sel = pd.read_csv(site_file)
# select subset of columns + create datetime index
fluxnet_sel_simple = fluxnet_sel[['TIMESTAMP_START','TIMESTAMP_END', 'NEE_VUT_REF']]
fluxnet_sel_simple .index = pd.to_datetime(fluxnet_sel_simple ['TIMESTAMP_START'],format='%Y%m%d%H%M')
fluxnet_sel_simple.index.names = ['time']


# Convert and resample
# FluxNet NEE_VUT_REF (umolCO2 m-2 s-1) to MiCASA (kgC m-2 s-1)
fluxnet_sel_final = fluxnet_sel_simple['NEE_VUT_REF']*1e-6*12.01*1e-3

# resample to 3-hourly per MiCASA
fluxnet_sel_final = fluxnet_sel_final.resample('3h').mean()
fluxnet_sel_final.name = 'FluxNET NEE (kgC m-2 s-1)'

# Create a list of unique dates from the site
time = fluxnet_sel_final.index
dates_unique = list({dt.date() for dt in time})
dates_unique.sort()

# Extract micasa data
data_path = 'micasa-data/daily-0.1deg-final/holding/3hrly/'
path_list = []

for date in dates_unique:
    f_year = str(date.year)
    f_month = f"{date.month:02}"
    filename = 'MiCASA_v1_flux_*' + date.strftime('%Y%m%d') + '.nc4'
    filepath = get_single_match(os.path.join(data_path,f_year,f_month,filename))
    path_list.append(filepath)

# open all paths
with xr.open_mfdataset(path_list)['NEE'] as ds:
    # Select grid closest to selected site
    ds_subset = ds.sel(lon=site_lon, lat=site_lat, method='nearest')

    # Prep data for writing to csv
    ds_out = ds_subset.squeeze(dim=['lat','lon'],drop=True).to_dataframe()
    ds_out = ds_out.rename(columns={'NEE': 'MiCASA NEE (kgC m-2 s-1)'})

    # Write to csv
    output_dir = 'output'
    output_filename = f'{site_ID}_micasa'
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)

    ds_out.to_csv(output_path)
