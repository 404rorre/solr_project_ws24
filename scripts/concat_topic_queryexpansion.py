import pandas as pd

final_topics = "topic_expansions/topics_final_queryexpansion.csv"
df_final = pd.read_csv(final_topics)

mesh_topics = "topic_expansions/topics_LLM_MESH_expansion.csv"
df_mesh = pd.read_csv(mesh_topics)

df_final["MESH_wide_search"]=df_mesh["MESH_wide_search"]
df_final["MESH_refine_search"]=df_mesh["MESH_refine_search"]

df_final.to_csv(final_topics, index=False)
print(df_final)