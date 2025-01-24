import pandas as pd
from tqdm import tqdm
from pysearch import QUERY


query_parser="defType"

CORES: list[str] = [

    "textEN_bm25_nltk_cit", 

]
#boosting = [2, 3, 4, 5]

VERSION_START: int = 3



#for boost_lim in [n/10 for n in range(1,11)]:


QUERIES: list[str] = [
    
    "(title:(query question narrative $5 $7)^1 OR abstract:(query question narrative $5 $7)^4) AND (title(query question $6) OR abstract:(query question $6)) & rq={!rerank reRankQuery=$rqq reRankDocs=1500 reRankWeight=1.0} & rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
    "(title:(query question narrative $5 $7)^1 OR abstract:(query question narrative $5 $7)^4) AND (title(query question narrative $6) OR abstract:(query question narrative $6)) & rq={!rerank reRankQuery=$rqq reRankDocs=1500 reRankWeight=1.0} & rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}"
    
    ]


df_topics =  pd.read_csv("topic_expansions/topics_final_queryexpansion.csv")
#topic_file = "data/topics/topics-rnd5.xml"

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
                    df_topics=df_topics,
                    #topicfile=topic_file,
                )        

        solr.run()
        #pbar.update(n)
        n += 1
VERSION_START += len(versions)


print("Finished runs")
print("Planned runs:\t",len(CORES)*len(versions))
print("Executed runs:\t",n)
