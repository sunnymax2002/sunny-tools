from models import *

import os
import json
import pandas as pd

script_filepath = os.path.abspath(__file__)

with open(r'C:\Users\sunnygup\OneDrive - Intel Corporation\Documents\Personal\personal_code\my_library\data.json') as fh:
	data = json.load(fh)



if 'tags' in data:
	tag_data = pd.DataFrame([Tag.model_validate(d).getHierName() for d in data['tags']])

print(data)
