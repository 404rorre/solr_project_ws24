from sys import exit
import os 
import pandas as pd
import numpy as np 


MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv") 
assert os.path.isfile(MAP_DIRECTORY), "map directory doesn't exist."

MAP: pd.DataFrame = pd.read_csv(MAP_DIRECTORY)

value_counts: dict = MAP["citation_count"].value_counts().to_dict()
amount_of_publications: int = sum(value_counts.values())

# Amount of publications not found on semantic scholar (/ with a citation count of -1)
amount_not_found: int = value_counts[-1]
print(f"{amount_not_found} publications ({round((amount_not_found / amount_of_publications)*100, 1)}) were not found on semantic scholar.")

# Amount of publications with a citation count larger than 0
amount_larger_than_zero: int = 0
for key, value in value_counts.items(): 
    if key == -1 or key == 0: 
        continue
    amount_larger_than_zero += value
print(f"{amount_larger_than_zero} publications ({round((amount_larger_than_zero / amount_of_publications)*100, 1)}%) have a citation_count larger than 0.​")


# Amount of publications with a citation count larger than 100
amount_larger_than_hundred: int = 0
for key, value in value_counts.items(): 
    if key < 100: 
        continue
    amount_larger_than_hundred += value
print(f"{amount_larger_than_hundred} publications ({round((amount_larger_than_hundred / amount_of_publications)*100, 1)}%) have a citation_count larger than 100.​")


# Average citation count (counting the -1s as 0s)
modified_value_counts: dict = value_counts.copy()
modified_value_counts[0] = modified_value_counts[0] + modified_value_counts[-1]
modified_value_counts.pop(-1)

weighted_sum = sum(key * value for key, value in modified_value_counts.items())
total_frequency = sum(modified_value_counts.values())
weighted_mean = weighted_sum / total_frequency
print(f"The average citation count is ~{round(weighted_mean, 1)}.")