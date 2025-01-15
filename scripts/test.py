import os
import pandas as pd
import plotly.express as px

f_path= os.path.join("data", "index", "metadata.csv")

df = pd.read_csv(f_path)
print(df)

print(len(df.loc[df["citation_count"]==99999]))
fig = px.histogram(df["citation_count"], log_y=True)
fig.show()