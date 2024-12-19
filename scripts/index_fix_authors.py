import pandas as pd
import numpy as np
import re 




# https://www.legendu.net/en/blog/regular-expression-python/

def change(x):
    x = str(x).strip('"')
    #x = x.replace(",", "")
    x = x.replace(";", "|")
    return x

f_path = "data/index/metadata.csv"

df = pd.read_csv(f_path)

print(df.dtypes)
print(df.shape)
#print(df["authors"])
df["authors"] = df["authors"].apply(change)

print(df)
print(df["authors"])
print(df["authors"].describe())
df.to_csv(f_path, index=False)

