import pandas as pd
import numpy as np
import re 
# https://www.legendu.net/en/blog/regular-expression-python/
def change_date(x):
    re_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(re_pattern, str(x)):
        return  f"0000-00-00" if np.nan else f"{x}-00-00"
    return x

def check_date(x):
    re_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(re_pattern, str(x)):
        print(x)
    #re_pattern = r"^\d{4}\.\d{2}\.\d{2}$" # nothing found -> indicates 
    #if re.match(re_pattern, str(x)):
    #    print(x)

f_path = "data/index/metadata.csv"

df = pd.read_csv(f_path)

print(df.dtypes)
print(df.shape)
#print(df["publish_time"])
#df["publish_time"] = df["publish_time"].apply(change_date)
df["publish_time"].apply(check_date)

print(df)
print(df["publish_time"])
print(df["publish_time"].describe())
df.to_csv(f_path, index=False)

#re_pattern = r"^\d{4}-\d{2}-\d{2}$"
#if re.match(re_pattern,"2024-01-01"):
#    print("yes")
