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
import pytz
from timezonefinder import TimezoneFinder


######### functions ############
def get_single_match(pattern):
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise ValueError("No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

# Function to convert local standard time (no DLS) time to UTC
tf = TimezoneFinder() 
def local_std_to_utc_std(df,col,lat,lon):
    def convert_row(row):
        # Find the timezone for the given lat/lon
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str is not None:
            timezone = pytz.timezone(timezone_str)
            # Localize datetime without DST
            standard_time = timezone.normalize(timezone.localize(row[col], is_dst=False))
            # Convert to UTC
            return standard_time.astimezone(pytz.utc)
        else:
            raise ValueError('Cannot determine site time zone')
            
    df['utc_time'] = df.apply(convert_row,axis=1)
    return df
    

# Arguments: Site ID, Fluxnet time step (HH or DD), and MiCASA variable to extract
parser = argparse.ArgumentParser(description='User-specified parameters')
parser.add_argument('site_ID', type=str,
                     help='FluxNet/AmeriFLUX Site Identifier (XX-XXX)')
parser.add_argument('timedelta', type=str, choices=['HH', 'DD'],
                     help='Time step used in Fluxnet Average Calculation')
parser.add_argument('variable_list', type=str, nargs='+',
                     help='MiCASA variable(s) desired for extraction (list all wanted)')
args = parser.parse_args()
site_ID = args.site_ID
timedelta = args.timedelta
micasa_var_list = args.variable_list
# print(micasa_var)

# Open site ID metadata and extract lat/lon
filepath = 'ameriflux-data/'
meta_file = filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
site_lat = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Latitude (degrees)'].values
site_lon = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Longitude (degrees)'].values
# print(site_lat, site_lon)

# Open site data and access time indices
site_file = get_single_match(filepath + 'AMF_' + site_ID + 
                            '_FLUXNET_SUBSET_*/AMF_' + site_ID + 
                            '_FLUXNET_SUBSET_' + timedelta + '*.csv')
# print(site_file)
fluxnet_sel = pd.read_csv(site_file)

# select subset of columns + convert to datetime objects

if timedelta == 'HH':
    fluxnet_sel_dates = fluxnet_sel.loc[:,['TIMESTAMP_START','TIMESTAMP_END']].copy()
    fluxnet_sel_dates['TIMESTAMP_START'] = pd.to_datetime(fluxnet_sel_dates['TIMESTAMP_START'],format='%Y%m%d%H%M')
    fluxnet_sel_dates['TIMESTAMP_END'] = pd.to_datetime(fluxnet_sel_dates['TIMESTAMP_END'],format='%Y%m%d%H%M')
    
    # Convert time to UTC
    fluxnet_sel_dates = local_std_to_utc_std(fluxnet_sel_dates,'TIMESTAMP_START',site_lat, site_lon)
    fluxnet_sel_dates = fluxnet_sel_dates.set_index('utc_time')

if timedelta == 'DD':
    fluxnet_sel_dates = fluxnet_sel.loc[:,['TIMESTAMP']].copy()
    fluxnet_sel_dates['TIMESTAMP'] = pd.to_datetime(fluxnet_sel_dates['TIMESTAMP'],format='%Y%m%d')
    fluxnet_sel_dates = fluxnet_sel_dates.set_index('TIMESTAMP')

# Create a list of unique dates from the site
time = fluxnet_sel_dates.index
dates_unique = list({dt.date() for dt in time})
dates_unique.sort()
# print(dates_unique)
# sys.exit()

# Extract micasa data
path = 'micasa-data/daily-0.1deg-final/holding/'
if timedelta == 'HH':
    data_path = path + '3hrly/'

if timedelta == 'DD':
    data_path = path + 'daily/'


path_list = []

for date in dates_unique:
    f_year = str(date.year)
    f_month = f"{date.month:02}"
    filename = 'MiCASA_v1_flux_*' + date.strftime('%Y%m%d') + '.nc4'
    filepath = get_single_match(os.path.join(data_path,f_year,f_month,filename))
    path_list.append(filepath)
 
path_list = path_list[0] # testing
# open all paths
with xr.open_mfdataset(path_list,data_vars=micasa_var_list) as ds:
    # Select grid closest to selected site
    ds_subset = ds.sel(lon=site_lon, lat=site_lat, method='nearest')
    print(ds_subset)
    sys.exit()


    # Prep data for writing to csv
    ds_out = ds_subset.squeeze(dim=['lat','lon'],drop=True).to_dataframe()
    ds_out = ds_out.rename(columns={micasa_var: f'MiCASA {micasa_var} ({ds_out[micasa_var].units})'})

    # Write to csv
    output_dir = 'output'
    output_filename = f'{site_ID}_micasa_{micasa_var}_{timedelta}.csv'
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)

    ds_out.to_csv(output_path)

