import numpy as np
import pandas as pd
import os 

METADATA_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "metadata_bak.csv")
MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")
assert os.path.isfile(METADATA_DIRECTORY), "metadata not found"
assert os.path.isfile(MAP_DIRECTORY), "map not found"

output_directory: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "metadata.csv")

METADATA: pd.DataFrame = pd.read_csv(METADATA_DIRECTORY, dtype={"doi":str})

MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY, dtype={"doi":str})

# check if dois are in the same order
v_flag = True
#for idx in range(len(METADATA)):
#    doi_metadata = METADATA.loc[idx, ["doi"]].array[0]
#    doi_map = MAP.loc[idx, ["doi"]].array[0]
#    
#    doi_metadata =  "" if np.nan or "nan" else doi_metadata
#    doi_map = "" if np.nan or "nan" else doi_map
#    
#    if not doi_metadata == doi_map:
#        print("note same on: ", idx)
#        v_flag = False
#        print(doi_metadata, doi_map)
#        break 

if v_flag:
    print("Perfect match on doi.")

    # Change all nan to -1 for differenatiation and data handling in solr indexing & querying
    MAP["citation_count"] = MAP["citation_count"].fillna(-1)
    MAP.loc[MAP["citation_count"]==-1,["citation_count"]]= 0

    # copy citation counts to metadata.csv
    METADATA["citation_count"] = MAP["citation_count"]

    print(METADATA)
    METADATA.to_csv(output_directory, index=False)