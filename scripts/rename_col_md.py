import pandas as pd

f_path = "../data/index/metadata.csv"

df = pd.read_csv(f_path)

if "id" in df.columns:
    print("Nothing done column exists already")
else :
    df.rename(columns={"cord_uid":"id"})

df.to_csv(f_path)