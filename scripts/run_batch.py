import pandas as pd
from tqdm import tqdm
from pysearch import QUERY



cores = [
    "textEN_bm25",  
]
boosting = [3, 4]

version_start= 10029


#for boost in boosting:
queries= [
    #"title:($11)",
    #"abstract:($11)",
    #f"title:($6)^{boost} AND abstract:($6)^1",
    f"title:(query)^2 OR abstract:(query)^1"
]
    
    
versions = [n for n in range(1, len(queries)+1)]
# df_topics =  pd.read_csv("topic_expansions/topics_llm_queryexpansion.csv")
topic_file = "data/topics/topics-rnd5.xml"
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
                    #df_topics=df_topics,
                    topicfile=topic_file
                )        

        solr.run()
        #pbar.update(n)
        n += 1
version_start += len(versions)


print("Finished runs")
print("Planned runs:\t",len(cores)*len(versions))
print("Executed runs:\t",n)