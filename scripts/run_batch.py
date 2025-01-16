import pandas as pd
from tqdm import tqdm
from pysearch import QUERY


query_parser="defType"

CORES: list[str] = [

    "textEN_bm25_citcount", 

]
#boosting = [2, 3, 4, 5]

VERSION_START: int = 109


#for boost_lim in [n/10 for n in range(1,11)]:


QUERIES: list[str] = [
    
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=2000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=2500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=3000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=3500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=4000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=4500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=5000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=5500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=6000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=6500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=7000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=7500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=8000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=8500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=9000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=9500 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}",
        "((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4) OR (title:($7)^1 OR abstract:($7)^4)) AND (title:($6) OR abstract:($6)) & rq={!rerank reRankQuery=$rqq reRankDocs=10000 reRankWeight=0.9}& rqq={!func v=div(log(sum(field(citation_count),1)),log(23426))}"

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
