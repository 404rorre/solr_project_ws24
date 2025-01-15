from unidecode import unidecode
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

#MERGE: pd.DataFrame = pd.merge(METADATA, MAP, left_on="doi", right_on="doi", how="left")

METADATA.to_csv(test_output_directory)