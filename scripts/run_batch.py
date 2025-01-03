import pandas as pd
from tqdm import tqdm
from pysearch import QUERY



cores = [
    "textEN_bm25",
    "textEN_DFI",
    "textEN_IBS",
    "textEN_LMDirichlet"    
]
queries= [
    #"title:($11)",
    #"abstract:($11)",
    "title:($11)^5 AND abstract:($11)^2",
    "title:($11)^5 OR abstract:($11)^2"
]
version_start= 24
versions = [
    n for n in range(1, len(queries)+1)
]
df_topics =  pd.read_csv("topic_expansions/topics_cluster_expansion.csv")
#topic_file = "data/topics/topics-rnd5.xml"
n = 0
for core in cores:
    #with tqdm(total=len(cores)*len(versions), desc="Running Settings", position=-0) as pbar: # maybe later too much time for debugging
    for version in versions:
        query = queries[version-1]
        print("Running...", f"Core:{core}", f"Version:{version+version_start-1}", f"Query:{query}", sep="\t")
        solr = QUERY(
                    version=str(version+version_start-1), 
                    core=core, 
                    rows=1000, 
                    url_query=query,
                    df_topics=df_topics,
                    #topicfile=topic_file
                )        

        solr.run()
        #pbar.update(n)
        n += 1


print("Finished runs")
print("Planned runs:\t",len(cores)*len(versions))
print("Executed runs:\t",n)