import pandas as pd

df_origin = pd.read_xml("data/topics/topics-rnd5.xml")
df_origin.to_csv("data/topics/topics-rnd5.csv", index=False)