from citation_count import get_citationCount_by_DOI

import os
import sys
import pandas as pd 

METADATA_DIRECTORY: str = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "index", "metadata.csv"))
metadata: pd.DataFrame = pd.read_csv(METADATA_DIRECTORY)

counter = 0
def retrieve_citation_count(row: pd.Series) -> int: 
    global counter
    counter += 1
    doi: str = str(row["doi"])
    # print(f"Checking '{doi}'...")
    print(counter)
    citation_count: int | None = get_citationCount_by_DOI(doi)
    if citation_count is None: 
        return 0
    return citation_count

metadata["citation_count"] = metadata.apply(retrieve_citation_count, axis=1)

# print(metadata.shape)
# Die metadaten.csv hat 192509 rows. In einer Minute schafft er ~110 Zeilen. anzahl_rows / 110 Zeilen = ~~1750.1 Minuten => ~29.17 Stunden...

