#!/usr/bin/env python
# Starting point for statistical analysis between MiCASA and FLUXNET datasets

import argparse
import pandas as pd
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
        raise ValueError("No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

#FIX: I'm not sure if I should throw away outliers for this?
'''
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
'''    

# Define misc variables
amer_filepath = '../ameriflux-data/'
mic_filepath = '../intermediates/'
timedelta = 'DD'

#FIX: I need to have a way to check if the stats were created for each site??
'''
############## Check if run is necessary #############
# Check if output file for the site already exists (quits if so)
output_dir = 'plots'
output_filename = f'{site_ID}_NEE_NPP.png'
output_path = os.path.join(output_dir, output_filename)

# If the file exists, exit the script
if os.path.exists(output_path):
    print(f"File for site {site_ID} already exists: {output_path}. Exiting.")
    sys.exit()  # Exit the script immediately
'''

#################### Import Flux Data ##############################
# Import site metadata csv
meta_file = amer_filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
fluxnet_meta = ameriflux_meta.loc[ameriflux_meta['AmeriFlux FLUXNET Data'] == 'Yes'] #use FLUXNET only
ids_list = fluxnet_meta['Site ID']
# print(type(ids_list))
# sys.exit()

# parser = argparse.ArgumentParser(description='Site ID')
# parser.add_argument('site_ID', metavar= 'site_ID', type=str,
#                     help='FluxNet Site ID')
# args = parser.parse_args()
# site_ID = args.site_ID
for site_ID in ids_list:
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

'''
## Mask bad QC values for NEE and GPP
## for daily FluxNet data, QC is fraction between 0-1, indicating percentage of measured and good quality gapfill data
fluxnet_final['NEE (kgC m-2 s-1)'] = fluxnet_final['NEE (kgC m-2 s-1)'].mask(fluxnet_sel_sub['NEE_VUT_REF_QC'] < 1, np.nan)
fluxnet_final['GPP (DT) (kgC m-2 s-1)'] = fluxnet_final['GPP (DT) (kgC m-2 s-1)'].mask(fluxnet_sel_sub['NEE_VUT_REF_QC'] < 1, np.nan)

# Mask GPP outliers
fluxnet_final = replace_outliers_with_nan(fluxnet_final,'GPP (DT) (kgC m-2 s-1)')
'''

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

NEE_RSME = (((NEE_ds.MiCASA - NEE_ds.FluxNet)**2).mean() **0.5)
print(NEE_RSME)

# NPP
NPP_ds = pd.DataFrame()
NPP_ds['MiCASA'] = micasa_ds['MiCASA NPP (kg m-2 s-1)']
NPP_ds['FluxNet DT GPP/2'] = fluxnet_final['GPP (DT) (kgC m-2 s-1)']/2
NPP_RSME = (((NPP_ds.MiCASA - NPP_ds['FluxNet DT GPP/2'])**2).mean() **0.5)
print(NPP_RSME)

