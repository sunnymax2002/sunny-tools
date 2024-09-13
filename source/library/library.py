# from models import *

import json
import pandas as pd

class InfoLib:
	LBL_TAG = 'tags'
	LBL_INFORMATION = 'informations'
	LBL_GRP = 'group'
	LBL_TYPE = 'type'
	LBL_TITLE = 'title'
	LBL_DESC = 'description'

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
	
	def report(self, prepare_data_func, header_type, show_desc = True, show_tags = True):
		df = self.info_df.copy()	
		dfv: pd.DataFrame = prepare_data_func(df)

		for _, row in dfv.iterrows():
			isHeading = '# ' if row[self.LBL_TYPE] == header_type else ''
			print(isHeading + row[self.LBL_TITLE])
			if show_tags:
				try:
					print('*' + ', '.join(row[self.LBL_TAG]) + '*')
				except:
					pass
			if show_desc:
				print(row[self.LBL_DESC])