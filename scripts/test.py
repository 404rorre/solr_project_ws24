import os
import pandas as pd
import numpy as np
import plotly.express as px

f_path= os.path.join("data", "index", "metadata.csv")

df = pd.read_csv(f_path)
print(df)

print(np.max(df.loc[df["citation_count"] < 99998,["citation_count"]]))
print(len(df.loc[df["citation_count"] == 99999]))
print(len(df.loc[df["citation_count"] == -1]))
print(df["citation_count"].describe())
fig = px.histogram(df["citation_count"], log_y=True)
fig.show()