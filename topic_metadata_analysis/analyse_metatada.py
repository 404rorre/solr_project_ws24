import pandas as pd

f_path = "data/2020-07-16/metadata.csv"

df = pd.read_csv(f_path)
print("Datentypen je Spalte (Keine Bereinigung)")
print(df.dtypes,"\n")
print("Fehlende Daten je Spalte")
print(df.isnull().sum(),"\n")



