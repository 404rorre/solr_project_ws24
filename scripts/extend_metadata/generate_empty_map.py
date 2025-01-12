import pandas as pd 
import os

# This particular script just generates the map_doi_citationcount.csv with a doi column and an empty citation_count column. 

METADATA_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "metadata.csv")
MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")


metadata: pd.DataFrame = pd.read_csv(METADATA_DIRECTORY)
map_df: pd.DataFrame = metadata["doi"].to_frame()
map_df["citation_count"] = None

map_df.to_csv(MAP_DIRECTORY)
