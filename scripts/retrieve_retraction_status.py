import os
import requests 
from tqdm import tqdm
import csv


CURRENT_DIR: str = os.path.dirname(__file__)
RETRACTION_DATA_DIR: str = os.path.join(CURRENT_DIR, "retraction_data.csv")


def update_retraction_data() -> bool: 
    print("Downloading updated retraction data...")
    url: str = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
    try: 
        response: requests.Response = requests.get(url, stream=True)
        if response.status_code != 200: 
            raise Exception()
        total_size = int(response.headers.get('content-length', 0))
        with open(RETRACTION_DATA_DIR, "wb") as file, tqdm(
            desc="Downloading",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                progress_bar.update(len(chunk))
        print("Successfully saved updated retraction_data.csv")
    except: 
        print("Failed to save retraction_data.csv")
        return False
    return True


def is_retracted(DOI: str) -> bool | None: 
    if not os.path.exists(RETRACTION_DATA_DIR): 
        update_retraction_data()
    result_row: dict | None = None
    try: 
        with open(RETRACTION_DATA_DIR, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                if row["OriginalPaperDOI"] == DOI.strip().lower(): 
                    result_row = row
                    break
    except:
        return None
    print(result_row)
    if result_row and result_row["RetractionNature"] == "Retraction": 
        return True
    return False
