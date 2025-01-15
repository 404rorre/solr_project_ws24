'''
This Script takes all "0" values from the map csv and retries them, to further differentiate between real zeros and not found dois
'''
import pandas 
import os 
import sys
from time import sleep
import requests


CSV_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")

df: pandas.DataFrame = pandas.read_csv(CSV_DIRECTORY)

class TimeOutError(Exception): 
    pass

index: int = 0
def fetch_citation_count(doi): 
    global index
    global amount_of_zeros
    index += 1
    print(f"\n{index} / {amount_of_zeros}")
    print(f"Checking '{doi}'")
    global df
    doi: str = str(doi)
    url: str = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi.strip()}?fields=citationCount"
    while True: 
        try: 
            response: requests.Response = requests.get(url)
            if response.status_code == 429: 
                raise(TimeOutError())
            break
        except TimeOutError: 
            wait_time: float = 120.0
            print(f"timed out. Waiting {wait_time} seconds.")
            sleep(wait_time)
            continue
        except: 
            print("Some other error occured")
            print(response.status_code)
            print(response.json())
    try: 
        citation_count: int = int(response.json()["citationCount"])
        print(citation_count)
        return citation_count
    except: 
        print("None")
        return None
    

print(df.head(10))
amount_of_zeros: int = (df["citation_count"] == 0.0).sum()
print(f"{amount_of_zeros = }")

df.loc[df["citation_count"] == 0.0, "citation_count"] = df.loc[df["citation_count"] == 0.0, "doi"].apply(fetch_citation_count)

df.to_csv(CSV_DIRECTORY)