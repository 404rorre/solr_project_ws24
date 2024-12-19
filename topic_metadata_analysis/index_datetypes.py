import pandas as pd
import numpy as np
import re 

f_path = "data/index/metadata.csv"

df = pd.read_csv(f_path)

print(df.dtypes)
print(df.shape)