from tqdm import tqdm
from pysearch import QUERY


cores = [
    "base_bm25"
]
queries= [
    "title:(query)",
    "abstract:(query)",
    "title:(query) abstract:(query)"
]
versions = [
    n for n in range(1, len(queries)+1)
]

n = 0
for core in cores:
    with tqdm(total=len(cores)*len(versions), desc="Running Settings", position=0) as pbar:
        for version in versions:
            query = queries[version-1]
            print("Running...", f"Core:{core}", f"Version:{version}", f"Query:{query}", sep="\t")
            solr = QUERY(version=str(version), 
                        core=core, 
                        rows=1000, 
                        url_query=query)
    
            solr.run()
            pbar.update(n)
            n += 1

print("finished runs")