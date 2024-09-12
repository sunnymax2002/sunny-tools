# from models import *

import os
import json
import pandas as pd

class InfoLib:
	LBL_TAG = 'tags'
	LBL_INFORMATION = 'informations'
	LBL_GRP = 'group'

	def __init__(self) -> None:
		self.info_df = None

	def load(self, json_path, grp_name, merge=True):
		with open(json_path) as fh:
			data = json.load(fh)

			if self.LBL_INFORMATION in data:
				info = pd.DataFrame(data[self.LBL_INFORMATION])
				info[self.LBL_GRP] = grp_name

				if merge and (self.info_df is not None):
					self.info_df = pd.concat([self.info_df, info])
				else:
					self.info_df = info

fq = r'D:\Code\git_repos\sunny-data\finance\investing\checklist.json'
fa = r'D:\Code\git_repos\sunny-data\finance\investing\analysis\kpit.json'

lib = InfoLib()
lib.load(fq, 'checklist')

lib.load(fa, 'KPITTECH.NS')

print(lib.info_df)

print('done')