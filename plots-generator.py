#!/usr/bin/env python
# Generate maps, NEE and NPP comparison plots for each site
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import hvplot.xarray
import hvplot.pandas
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import glob
import os

######### functions ############
# Define a single match file location function
def get_single_match(pattern):
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise ValueError(f"No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

######### input arguments ############
# Input site ID
parser = argparse.ArgumentParser(description='User-specified parameters')
parser.add_argument('site_ID', type=str,
                     help='FluxNet/AmeriFLUX Site Identifier (XX-XXX)')
site_ID = args.site_ID

# Define misc variables
amer_filepath = 'ameriflux-data/'
mic_filepath = 'intermediates/'
timedelta = 'DD'

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

## Mask bad NEE QC values
## for daily FluxNet data, QC is fraction between 0-1, indicating percentage of measured and good quality gapfill data
fluxnet_final['NEE (kgC m-2 s-1)'] = fluxnet_final['NEE (kgC m-2 s-1)'].mask(fluxnet_sel_sub['NEE_VUT_REF_QC'] < 1, np.nan)

# GPP
## FluxNet GPP in DD (gC m-2 d-1) to MiCASA (kgC m-2 s-1)
fluxnet_final['GPP (DT) (kgC m-2 s-1)'] = fluxnet_sel_sub['GPP_DT_VUT_REF']*1e-3/86400
fluxnet_final['GPP (NT) (kgC m-2 s-1)'] = fluxnet_sel_sub['GPP_NT_VUT_REF']*1e-3/86400

############ Import Preprocessed Micasa Data ################
micasa_ds = pd.DataFrame()
for variable in ['NEE', 'NPP']:
    filename = f'{site_ID}_micasa_{variable}_{timedelta}.csv'
    path = os.path.join(mic_filepath, filename)
    ds = pd.read_csv(path,index_col=0)
    ds.index = pd.to_datetime(ds.index)
    varname = variable + ' (kgC m-2 s-1)'
    micasa_ds[varname] = ds

############## Append datasets #########################
# Make clean dataframe and append together
## NEE
NEE_ds = pd.DataFrame()
NEE_ds['MiCASA'] = micasa_ds['NEE (kgC m-2 s-1)']
NEE_ds['FluxNet'] = fluxnet_final['NEE (kgC m-2 s-1)']

## NPP
NPP_ds = pd.DataFrame()
NPP_ds['MiCASA'] = micasa_ds['NPP (kgC m-2 s-1)']
NPP_ds['FluxNet DT NPP/2'] = fluxnet_final['GPP (DT) (kgC m-2 s-1)']/2

## Subsetting? 
# NPP_ds = NPP_ds[NPP_ds.index >= '2018-01-01']

######### Create plots ########################
# Create a subplot grid with specific width ratios
fig, axs = plt.subplots(4, 1, 
                         # subplot_kw={'projection': proj}, 
                         gridspec_kw={'height_ratios': [1, 2,0.25,2],
                                      'hspace': 0.01},
                         figsize=(10, 12)) 

# Define the map projection
proj = ccrs.PlateCarree()

# Subset CONUS
min_lon, max_lon = -125, -65
min_lat, max_lat = 25, 50

axs[0].axis('off')
axs[0] = plt.subplot(4, 1, 1, projection=proj,frameon=False)
axs[0].set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
axs[0].add_feature(cfeature.STATES)

site_lat = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Latitude (degrees)'].values
site_lon = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID, 'Longitude (degrees)'].values
axs[0].scatter(site_lon,site_lat,
       marker='*', 
       s=500,
       color='yellow',
       edgecolor='black',
               zorder=3)
# axs[0].annotate(site_ID, (site_lon + 2,site_lat+2),
#             color='red',
#             bbox=dict(facecolor='white',edgecolor='None', pad=0.1,
#                      )
#            )

NEE.plot(ax=axs[1],ylabel = 'NEE\n(kgC m$^{-2}$ s$^{-1}$)')

axs[2].set_visible(False)

NPP.plot(ax=axs[3],ylabel = 'NPP\n(kgC m$^{-2}$ s$^{-1}$)')

date_format = mdates.DateFormatter('%b %Y')
for i in range(1,4,2):
    axs[i].xaxis.set_major_formatter(date_format)
    axs[i].set_xlabel('') 
fig.suptitle(f'{site_ID}',y=0.9,fontsize=14)

output_dir = 'plots'
output_filename = f'{site_ID}_NEE_NPP.png'
output_path = os.path.join(output_dir, output_filename)

fig.savefig(output_path)