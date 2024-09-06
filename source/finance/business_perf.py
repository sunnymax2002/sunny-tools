import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import datetime

import context

from utils.io import ReadConfig
from screener import *

logging.basicConfig(level=logging.INFO)

# Common figure settings
PAGE_DIMS = (16, 9) # (11.7, 8.27)    # A4
plt.style.use("dark_background")

config = ReadConfig()

DATA_DIR_NAME = 'finance/screener'
OUTPUT_DIR_NAME = 'finance/output'

# Find all XLSX files in data directory
data_dir = Path(config['data_dir'], DATA_DIR_NAME)
out_dir = Path(config['data_dir'], OUTPUT_DIR_NAME)

companies = None
# companies = ['Tanla Platforms']
# companies = ['Angel One', 'Avenue Super', 'Hind. Unilever', 'Asian Paints', 'Tanla Platforms',
            #  'C D S L', 'L&T Technology', 'Larsen & Toubro', 'Rategain Travel', 'TCS', 'Polycab India', 'Titan Company']

# Those which could not be processed
not_processed = []

if companies is not None:
    data_files = {c:None for c in companies}
else:
    data_files = {fpath.stem:fpath for fpath in data_dir.iterdir()}

for company_name, fpath in data_files.items():
    logging.info(f'Analyzing {company_name}')

    if fpath is None:
        fpath = Path(data_dir, f'{company_name}.xlsx')

    data = read_screener_xls(fpath)
    if data is None:
        not_processed.append(company_name)
        continue

    data[INC_CE] = (data[FIXED_ASSETS].diff() + (data[OTHER_ASSETS] - data[OTHER_LIABILITIES]).diff()) / (data[FIXED_ASSETS] + (data[OTHER_ASSETS] - data[OTHER_LIABILITIES]))
    data[FCFF] = data[CFO] - data[INC_CE] - data[TAX]
    data[FM] = data[FCFF] / data[SALES]
    data[SALES_GR] = data[SALES].diff() / data[SALES]
    data[INV2CE] = data[INVESTMENTS] / (data[EQUITY] + data[RESERVES] + data[DEBT])

    # Convert to percentages, and change x-labels to Mar-YYYY
    useful_cols = [SALES_GR, OPM, INC_CE, ROCE, FM]
    result = data[useful_cols] * 100

    # Drop non-date columns e.g. Epoch.1/.2 etc
    result[IDX_TYPE] = result.apply(lambda x: type(x.name), axis=1)
    result = result.loc[result[IDX_TYPE] == datetime.datetime]

    new_lbls = {d:d.strftime('%b-%Y') for d in result.index}
    result.rename(index=new_lbls, inplace=True)

    # Turns off interactive plotting
    plt.ioff()

    # Melt for seaborn
    df_melted = pd.melt(result.reset_index(), id_vars='index', value_vars=useful_cols)

    fig, ax = plt.subplots(figsize=PAGE_DIMS)
    ax = sns.barplot(x="index", y="value", hue="Narration", data=df_melted, ax=ax)
    ax.set(title=company_name)

    ax.set_ylabel('Percentage')
    ax.set_xlabel('Financial Year End')
    plt.xticks(rotation=90)
    plt.grid()

    # Save to file
    # fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(Path(out_dir, f'{company_name}.png'), dpi=600) 

    # plt.show()

    # Close fig
    plt.close(fig)

if len(not_processed) > 0:
    logging.error('Could not process the following companies:')
    logging.info(not_processed)