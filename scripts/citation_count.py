import requests


def get_citationCount_by_paperID(paperID: str) -> int | None: 
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paperID.strip()}?fields=citationCount"
    try: 
        response: requests.Response = requests.get(url)
        if response.status_code != 200: 
            raise Exception()
        return int(response.json()["citationCount"])
    except: 
        return None


def get_citationCount_by_DOI(DOI: str) -> int | None: 
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI.strip()}?fields=citationCount"
    try: 
        response: requests.Response = requests.get(url)
        if response.status_code != 200: 
            raise Exception()
        return int(response.json()["citationCount"])
    except: 
        return None
