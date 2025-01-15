import numpy as np
import pandas as pd
import os 

METADATA_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "metadata.csv")
MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")
assert os.path.isfile(METADATA_DIRECTORY), "metadata not found"
assert os.path.isfile(MAP_DIRECTORY), "map not found"

test_output_directory: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "mapped_test.csv")

METADATA: pd.DataFrame = pd.read_csv(METADATA_DIRECTORY, dtype={"doi":str})

MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY, dtype={"doi":str})

METADATA["citation_count"] = MAP["citation_count"]
#MERGE: pd.DataFrame = pd.merge(METADATA, MAP, left_on="doi", right_on="doi", how="left", suffixes=('', '_right'))

v_flag = True
for idx in range(len(METADATA)):
    doi_metadata = METADATA.loc[idx, ["doi"]].array[0]
    doi_map = MAP.loc[idx, ["doi"]].array[0]
    
    doi_metadata =  "" if np.nan or "nan" else doi_metadata
    doi_map = "" if np.nan or "nan" else doi_map
    
    if not doi_metadata == doi_map:
        print("note same on: ", idx)
        v_flag = False
        print(doi_metadata, doi_map)
        break 

if v_flag:
    print("Perfect match on doi.")

METADATA.to_csv(test_output_directory)