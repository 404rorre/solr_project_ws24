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
    response: requests.Response = requests.get(url)
    while True: 
        try: 
            if response.status_code == 429: 
                print("too many requests, asking again...")
                continue
            if response.status_code != 200: 
                raise Exception()
            return int(response.json()["citationCount"])
        except: 
            if "not found" in response.json()["error"]: 
                return None
            print(f"{response.json() = }")
            print(f"{response.status_code = }")
            return None


if __name__ == "__main__": 
    print(get_citationCount_by_DOI("10.1186/1471-2334-1-6"))
