from citation_count import get_citationCount_by_DOI

import os
import sys
import pandas as pd 
from concurrent.futures import ThreadPoolExecutor


MAP_CSV_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcont.csv")
map_df: pd.DataFrame = pd.read_csv(MAP_CSV_DIRECTORY)


counter: int = 0
def get_api_response(doi: str) -> int:
    global counter
    counter += 1
    print(f"{counter}")
    citation_count: int | None = get_citationCount_by_DOI(doi)
    citation_count = 0 if citation_count is None else citation_count
    print(f"{counter}\t{citation_count}")
    return citation_count

# Function to apply to the rows in parallel
def apply_parallel(row):
    return get_api_response(row['doi'])

# Use ThreadPoolExecutor to parallelize the requests
def process_in_parallel(df: pd.DataFrame) -> pd.DataFrame:
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(apply_parallel, [row for _, row in df.iterrows()]))
    
    # Add results to a new column
    df['citation_count'] = results
    return df


def save_to_map_csv(df: pd.DataFrame) -> None: 
    pass

# Process DataFrame in parallel
metadata: pd.DataFrame = process_in_parallel(map_df)

metadata.to_csv(MAP_CSV_DIRECTORY)

# often causes error 429 - too many requests. 
# New idea: periodically map a citation count in a seperate csv file to every existing doi. These can then be combined before every run into a proper "enriched" metadata.csv
