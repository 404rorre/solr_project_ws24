import pandas as pd

df = pd.read_xml("data/topics/topics-rnd5.xml")
df.to_csv("data/topics/topics-rnd5.csv", index=False)