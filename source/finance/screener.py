import pandas as pd
import logging
import numpy as np

import context
from utils.io import get_xls_data

SALES = 'Sales'
SALES_GR = 'Sales Growth Rate'
OPM = 'OPM'
ROCE = 'Return on Capital Emp'
FCFF = 'Free Cash Flow to Firm (FCFF)'
FM = 'FCFF as % of Sales'
INV2CE = 'Investments as % of CE'
INC_CE = 'Incremental Capital Employed (CE) as % of Total CE'

CFO = 'Cash from Operating Activity'
FIXED_ASSETS = 'Net Block'
OTHER_ASSETS = 'Other Assets'
OTHER_LIABILITIES = 'Other Liabilities'
INVESTMENTS = 'Investments'
EQUITY = 'Equity Share Capital'
RESERVES = 'Reserves'
DEBT = 'Borrowings'
TAX = 'Tax'

IDX_TYPE = 'idx_type'

def read_screener_xls(fpath) -> pd.DataFrame:
    srow = 3
    erow = 19
    sheet_name = 'Profit & Loss'
    pnl = get_xls_data(fpath, srow, erow, sheet_name)
    pnl.drop(['Trailing', 'Best Case', 'Worst Case'], axis=1, inplace=True)
    # pnl.info()
    logging.debug(pnl)

    srow = 3
    erow = 24
    sheet_name = 'Balance Sheet'
    bs = get_xls_data(fpath, srow, erow, sheet_name)
    # bs.info()
    logging.debug(bs)

    srow = 3
    erow = 7
    sheet_name = 'Cash Flow'
    cf = get_xls_data(fpath, srow, erow, sheet_name)
    # cf.info()
    logging.debug(cf)

    data = pd.concat([pnl, bs, cf]).transpose()
    logging.debug(data)
    # data.info()

    # Check if null values read
    non_null = np.any(data.count(axis=1))
    if not non_null:
        logging.error('All values read as null, open and save XLSX and try again')
        return None
    
    return data
