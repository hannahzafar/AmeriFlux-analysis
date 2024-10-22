# Extract micasa data as csv for plotting
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr


######### functions ############
def get_single_match(pattern):
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise ValueError(f"No matches found")
    else:
        raise ValueError(f"Multiple matches found: {matches}")

site_ID = # argparse

filepath = 'ameriflux-data/'
meta_file = filepath + 'AmeriFlux-site-search-results-202410071335.tsv'
ameriflux_meta = pd.read_csv(meta_file, sep='\t')
site_meta = ameriflux_meta.loc[ameriflux_meta['Site ID'] == site_ID]


site_file = get_single_match(filepath + 'AMF_' + site_ID + 
                            '_FLUXNET_SUBSET_*/AMF_' + site_ID + '_FLUXNET_SUBSET_HH_*.csv')
fluxnet_sel = pd.read_csv(site_file)
# select subset of columns + create datetime index
fluxnet_sel_simple = fluxnet_sel[['TIMESTAMP_START','TIMESTAMP_END', 'NEE_VUT_REF']]
fluxnet_sel_simple .index = pd.to_datetime(fluxnet_sel_simple ['TIMESTAMP_START'],format='%Y%m%d%H%M')
fluxnet_sel_simple.index.names = ['time']

# Create a list of unique dates from the site
time = fluxnet_sel_final.time.to_index()
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




