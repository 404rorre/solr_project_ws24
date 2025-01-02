import pandas as pd

# first simple cluster expansion no additional Query Expansion used.
df_origin = pd.read_xml("data/topics/topics-rnd5.xml")
df = pd.read_csv("data/topics/topics_clustered.csv")
print(df)
# Enhance clustered queries 
df["query_long"]= df["query"]
df["query"]= df_origin["query"]
df["question"] = df_origin["question"]
df["narrative"] = df_origin["narrative"]
df["clustered_terms"] = ["0" for _ in range(len(df)) ]
df["number"] = df["qid"]
print(df_origin.head(2))
print(df)

topics = df["qid"].tolist()
print(topics)

for topic in topics:
    cluster = df.loc[df["qid"]==topic,"cluster"].item()
    queries = df.loc[df["cluster"]==cluster, "query"].tolist()
    cluster_query = " ".join(set(term for query in queries for term in query.split()))
    df.loc[df["qid"]==topic, "clustered_terms"]=cluster_query
    
df.to_csv("data/topics/topics_cluster_expansion", index=False)
print(df.columns)