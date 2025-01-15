import pandas as pd
import os 

METADATA_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "metadata.csv")
MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")
assert os.path.isfile(METADATA_DIRECTORY), "metadata not found"
assert os.path.isfile(MAP_DIRECTORY), "map not found"

test_output_directory: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "index", "mapped_test.csv")

METADATA: pd.DataFrame = pd.read_csv(METADATA_DIRECTORY)
MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY)

MERGE: pd.DataFrame = METADATA.merge(MAP, on="doi", how="left")

MERGE.to_csv(test_output_directory)