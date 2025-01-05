import pandas as pd
from tqdm import tqdm
from pysearch import QUERY



CORES: list[str] = [
    "textEN_bm25", 
]
#boosting = [2, 3, 4, 5]

VERSION_START: int = 10001


#for boost in boosting:


QUERIES: list[str] = [
    "title:(query)",
    "abstract:(query)",
    "title:(query) AND abstract:(query)",
    "title:(query) OR abstract:(query)",
    
    #f"title:(query)^1 AND abstract:(query)^{boost}",
    #f"title:(query)^1 OR abstract:(query)^{boost}"
]


# df_topics =  pd.read_csv("topic_expansions/topics_llm_queryexpansion.csv")
topic_file = "data/topics/topics-rnd5.xml"

##################################################################################################
##################################################################################################
versions = [
n for n in range(1, len(QUERIES)+1)
]

n = 0
for core in CORES:
    #with tqdm(total=len(CORES)*len(versions), desc="Running Settings", position=-0) as pbar: # maybe later too much time for debugging
    for version in versions:
        query = QUERIES[version-1]
        print("Running...", f"Core:{core}", f"Version:{version+VERSION_START-1}", f"Query:{query}", sep="\t")
        solr = QUERY(
                    version=str(version+VERSION_START-1), 
                    core=core, 
                    rows=1000, 
                    url_query=query,
                    #df_topics=df_topics,
                    topicfile=topic_file
                )        

        solr.run()
        #pbar.update(n)
        n += 1
VERSION_START += len(versions)


print("Finished runs")
print("Planned runs:\t",len(CORES)*len(versions))
print("Executed runs:\t",n)
