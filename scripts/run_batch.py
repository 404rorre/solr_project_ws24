import pandas as pd
from tqdm import tqdm
from pysearch import QUERY



CORES: list[str] = [

    "textEN_bm25", 

]
#boosting = [2, 3, 4, 5]

VERSION_START: int = 74


#for boost in boosting:


QUERIES: list[str] = [
    #["title:($2~)", " OR ", "abstract:($2~)"],
    #["title:($2*)", " OR ", "abstract:($2*)"],
    #["title:($2~)", " AND ", "abstract:($2~)"],
    #["title:($2*)", " AND ", "abstract:($2*)"],
    
    '({!edismax qf="title abstract" pf2="title abstract"}query)',
    '({!edismax qf="title abstract" pf3="title abstract"}query)',
    '({!edismax qf="title abstract" pf2="title" pf3="abstract" ps3=5}query)',
    '({!edismax qf="title abstract" mm="2<75%25 5<60%25 7<40%25"}query)',
    '(({!edismax qf="title" mm="2<75%25 5<60%25 7<40%25"}query) AND ({!edismax qf="abstract" mm="3<1 5<75%25 7<50%25"}query))',
    '({!edismax qf="title^1 abstract^4" pf2="title abstract"}query)',
    '({!edismax qf="title^1 abstract^4" pf3="title abstract"}query)'
    
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
