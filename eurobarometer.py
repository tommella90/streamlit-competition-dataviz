import pandas as pd
import parquet

#%%
df = pd.read_stata('data/harmonised_EB_2004-2021.dta', convert_categoricals=False)

#%%
df.to_parquet("data_clean/eurobarometer.parquet.gzip", compression="gzip")