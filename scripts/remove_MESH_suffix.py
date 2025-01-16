import pandas as pd

f_path = "topic_expansions/topics_LLM_MESH_expansion.csv"
df = pd.read_csv(f_path)

df["MESH_wide_search"] = df["MESH_wide_search"].apply(lambda x: x.replace("[MeSH]", ""))
df["MESH_wide_search"] = df["MESH_wide_search"].apply(lambda x: x.replace("[Publication Type]", ""))
df["MESH_wide_search"] = df["MESH_wide_search"].apply(lambda x: x.replace(",", ""))
df["MESH_refine_search"] = df["MESH_refine_search"].apply(lambda x: x.replace("[MeSH]", ""))
df["MESH_refine_search"] = df["MESH_refine_search"].apply(lambda x: x.replace("[Publication Type]", ""))
df["MESH_refine_search"] = df["MESH_refine_search"].apply(lambda x: x.replace(",", ""))

df.to_csv(f_path, index=False)