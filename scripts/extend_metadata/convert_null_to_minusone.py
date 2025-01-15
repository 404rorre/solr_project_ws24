import pandas as pd
import os

MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")
assert os.path.isfile(MAP_DIRECTORY), "unable to find map_doi_citationcount.csv"

MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY)

MAP = MAP.fillna(-1)

MAP.to_csv(MAP_DIRECTORY)