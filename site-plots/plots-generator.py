#!/usr/bin/env python
# Generate maps, NEE and NPP comparison plots for each site
import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import glob
import os
import sys

######### functions ############
# Define a single match file location function
def get_single_match(pattern):
    """
    Find exactly one file that matches the glob pattern.
    
    Uses glob.glob to find files matching the given pattern. Returns the single
    match if exactly one is found. Raises ValueError if no matches or multiple
    matches are found.
    
    Args:
        pattern (str): A glob pattern to search for files
        
    Returns:
        str: Path to the single matched file
        
    Raises:
        ValueError: If zero or multiple matches are found
    """
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise ValueError(f"No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

def replace_outliers_with_nan(df, column):
    """Replaces outliers in a DataFrame column with NaN.

    Args:
        df (pd.DataFrame): The DataFrame.
        column (str): The column name to check for outliers.

    Returns:
        pd.DataFrame: The DataFrame with outliers replaced by NaN.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df[column] = df[column].mask((df[column] < lower_bound) | (df[column] > upper_bound), np.nan)
    return df
    
######### input arguments ############
# Input site ID
parser = argparse.ArgumentParser(description='User-specified parameters')
parser.add_argument('site_ID', type=str,
                     help='FluxNet/AmeriFLUX Site Identifier (XX-XXX)')
args = parser.parse_args()
site_ID = args.site_ID

# Define misc variables
amer_filepath = '../ameriflux-data/'
mic_filepath = 'preprocess-data/intermediates/'
timedelta = 'DD'


############## Check if run is necessary #############
# Check if output file for the site already exists (quits if so)
output_dir = 'plots'
output_filename = f'{site_ID}_NEE_NPP.png'
output_path = os.path.join(output_dir, output_filename)
    
# If the file exists, exit the script
if os.path.exists(output_path):
    print(f"File for site {site_ID} already exists: {output_path}. Exiting.")
    sys.exit()  # Exit the script immediately

#################### Import Flux Data ##############################
# Import site metadata csv
meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only

# Import selected site daily subset data
site_lat = fluxnet_meta.loc[fluxnet_meta['Site ID'] == site_ID, 'Latitude (degrees)'].values
site_lon = fluxnet_meta.loc[fluxnet_meta['Site ID'] == site_ID, 'Longitude (degrees)'].values

sel_file = get_single_match(amer_filepath + 'AMF_' + site_ID + '_FLUXNET_SUBSET_*/AMF_' + site_ID + '_FLUXNET_SUBSET_' + timedelta + '_*.csv')
fluxnet_sel = pd.read_csv(sel_file)
fluxnet_sel_sub = fluxnet_sel.loc[:,['TIMESTAMP','NEE_VUT_REF','NEE_VUT_REF_QC','GPP_NT_VUT_REF', 'GPP_DT_VUT_REF']].copy()
fluxnet_sel_sub['TIMESTAMP'] = pd.to_datetime(fluxnet_sel_sub['TIMESTAMP'],format='%Y%m%d')
fluxnet_sel_sub = fluxnet_sel_sub.set_index('TIMESTAMP')

# Make a clean output df
fluxnet_final = pd.DataFrame()

# NEE
## Convert units
## FluxNet NEE_VUT_REF in DD (gC m-2 d-1) to MiCASA (kgC m-2 s-1)
fluxnet_final['NEE (kgC m-2 s-1)'] = fluxnet_sel_sub['NEE_VUT_REF']*1e-3/86400

# GPP
## FluxNet GPP in DD (gC m-2 d-1) to MiCASA (kgC m-2 s-1)
fluxnet_final['GPP (DT) (kgC m-2 s-1)'] = fluxnet_sel_sub['GPP_DT_VUT_REF']*1e-3/86400
fluxnet_final['GPP (NT) (kgC m-2 s-1)'] = fluxnet_sel_sub['GPP_NT_VUT_REF']*1e-3/86400

## Mask bad QC values for NEE and GPP
## for daily FluxNet data, QC is fraction between 0-1, indicating percentage of measured and good quality gapfill data
fluxnet_final['NEE (kgC m-2 s-1)'] = fluxnet_final['NEE (kgC m-2 s-1)'].mask(fluxnet_sel_sub['NEE_VUT_REF_QC'] < 1, np.nan)
fluxnet_final['GPP (DT) (kgC m-2 s-1)'] = fluxnet_final['GPP (DT) (kgC m-2 s-1)'].mask(fluxnet_sel_sub['NEE_VUT_REF_QC'] < 1, np.nan)

# Mask GPP outliers
fluxnet_final = replace_outliers_with_nan(fluxnet_final,'GPP (DT) (kgC m-2 s-1)')

############ Import Preprocessed Micasa Data ################
filename = f'{site_ID}_micasa_{timedelta}.csv'
path = os.path.join(mic_filepath, filename)
micasa_ds = pd.read_csv(path,index_col=0, parse_dates=True)

############## Append datasets #########################
# Make clean dataframe and append together
## NEE
NEE_ds = pd.DataFrame()
NEE_ds['MiCASA'] = micasa_ds['MiCASA NEE (kg m-2 s-1)']
NEE_ds['FluxNet'] = fluxnet_final['NEE (kgC m-2 s-1)']

## NPP
NPP_ds = pd.DataFrame()
NPP_ds['MiCASA'] = micasa_ds['MiCASA NPP (kg m-2 s-1)']
NPP_ds['FluxNet DT GPP/2'] = fluxnet_final['GPP (DT) (kgC m-2 s-1)']/2


######### Create plots ########################
# Create a subplot grid with specific width ratios
fig, axs = plt.subplots(4, 1, 
                         # subplot_kw={'projection': proj}, 
                         gridspec_kw={'height_ratios': [1.2, 2,0.25,2],
                                      'hspace': 0.01},
                         figsize=(10, 12)) 

# Define the map projection
proj = ccrs.PlateCarree()

# Extract site lat/lon
site_lat = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Latitude (degrees)'].values
site_lon = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Longitude (degrees)'].values

# Pick map location based on location of site
if site_lat >= 20:
    # North America extents
    min_lon, max_lon = -170, -57
    min_lat, max_lat = 25, 74

else:
    # South America extents
    min_lon, max_lon = -90, -30
    min_lat, max_lat = -60, 12

axs[0].axis('off')
axs[0] = plt.subplot(4, 1, 1, projection=proj,frameon=False)
axs[0].set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
axs[0].coastlines()
axs[0].scatter(site_lon,site_lat,
       marker='*', 
       s=300,
       color='yellow',
       edgecolor='black',
               zorder=3)


NEE_ds.plot(ax=axs[1],ylabel = 'NEE\n(kgC m$^{-2}$ s$^{-1}$)')
# Format x-axis labels
axs[1].xaxis.set_major_locator(mdates.AutoDateLocator())
# Disable minor ticks completely
axs[1].tick_params(axis='x', which='minor', labelsize=0, labelcolor='none')

axs[2].set_visible(False)

NPP_ds.plot(ax=axs[3],ylabel = 'NPP\n(kgC m$^{-2}$ s$^{-1}$)')
# Format x-axis labels
axs[3].xaxis.set_major_locator(mdates.AutoDateLocator())
# Disable minor ticks completely
axs[3].tick_params(axis='x', which='minor', labelsize=0, labelcolor='none')


date_format = mdates.DateFormatter('%b %Y')
for i in range(1,4,2):
    axs[i].xaxis.set_major_formatter(date_format)
    axs[i].set_xlabel('') 
fig.suptitle(f'{site_ID}',y=0.9,fontsize=14)

output_path = os.path.join(output_dir, output_filename)

fig.savefig(output_path)
print(f"Plot written to: {output_path}")
