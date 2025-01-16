import pandas as pd
import os

MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")

MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY)
value_counts = MAP["citation_count"].value_counts()

wanted_citation_count: int = -1
amount_of_appearances: int = int(value_counts[wanted_citation_count])

print(f"The citation count of '{wanted_citation_count}' appears {amount_of_appearances} times in the map-csv!")
