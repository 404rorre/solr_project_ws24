import pandas as pd
from tqdm import tqdm
from pysearch import QUERY


query_parser="defType"

CORES: list[str] = [

    "textEN_bm25", 

]
#boosting = [2, 3, 4, 5]

VERSION_START: int = 103


#for boost in boosting:


QUERIES: list[str] = [
    #["title:($2~)", " OR ", "abstract:($2~)"],
    #["title:($2*)", " OR ", "abstract:($2*)"],
    #["title:($2~)", " AND ", "abstract:($2~)"],
    #["title:($2*)", " AND ", "abstract:($2*)"],
    

"((title:(query)^1 OR abstract:(query))^4 OR (title:($5) OR abstract:($5))) OR (title:($6) OR abstract:($6))",
"((title:(query) OR abstract:(query)) OR (title:($5)^1 OR abstract:($5)^4)) OR (title:($6) OR abstract:($6))",
"((title:(query)^1 OR abstract:(query)^4) OR (title:($5)^1 OR abstract:($5)^4)) OR (title:($6) OR abstract:($6))",
"((title:(query) OR abstract:(query)) OR (title:($5)^1 OR abstract:($5)^4)) OR (title:($6)^1 OR abstract:($6)^4)",
"(title:($5) OR abstract:($5)) OR (title:($6) OR abstract:($6))"
    
]


df_topics =  pd.read_csv("topic_expansions/topics_llm_queryexpansion.csv")
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
