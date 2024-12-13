import pandas as pd
df = pd.read_csv("data/index/metadata.csv")
df[:3].to_csv("metadata_only_3rows.csv")