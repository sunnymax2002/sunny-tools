# Uses Library module to report analysis for businesses

from library import *

fq = r'D:\Code\git_repos\sunny-data\finance\investing\checklist.json'
fa = r'D:\Code\git_repos\sunny-data\finance\investing\analysis\kpit.json'

lib = InfoLib()
lib.load(fq, 'checklist')

lib.load(fa, 'KPITTECH.NS')

print(lib.info_df)

# Filter and Sort
def prepare_data_for_reporting(df: pd.DataFrame):
    col_type = 'type'
    col_id = 'id'
    type_filt = ['question', 'answer']

    df = df[df[col_type].isin(type_filt)]

    df[col_type] = pd.Categorical(df[col_type], type_filt)
    df.sort_values(by=[col_id, col_type], inplace=True)

    # Fill NaN
    df.fillna('', inplace=True)

    return df

lib.report(prepare_data_func=prepare_data_for_reporting, header_type='question')

print('done')