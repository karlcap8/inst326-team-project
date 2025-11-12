#Karl add HeaderNormalizer here i believe



#Harrang:
from research_data_lib import cast_row_types

 class PIIRemover(Transformer):
 	def __init__(self, columns):
         super().__init__("PIIRemover")
     	self.columns = columns
 	@property
 	def required_columns(self): return []
 	def _apply(self, df): return df.drop(columns=self.columns, errors="ignore")

 class TypeCaster(Transformer):
 	def __init__(self, type_map):
         super().__init__("TypeCaster")
     	self.type_map = type_map
 	@property
 	def required_columns(self): return list(self.type_map.keys())
 	def _apply(self, df):
     	rows = df.to_dict(orient="records")
     	from research_data_lib import cast_row_types
     	casted = [cast_row_types(r, self.type_map) for r in rows]
     	import pandas as pd
     	return pd.DataFrame(casted)
