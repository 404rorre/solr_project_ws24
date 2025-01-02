import pandas as pd

f_path = "data/index/metadata.csv"

df = pd.read_csv(f_path)

print(df)

if "id" in df.columns:
    print("Nothing done column exists already")
else :
    df = df.rename(columns={"cord_uid":"id"})

print(df)
df.to_csv(f_path, index=False)

print("Changed Column successfully!")