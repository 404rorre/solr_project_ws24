
import os
import asyncio
import aiohttp
import pandas as pd
from aiohttp import ClientSession
import time

# Path to the CSV file
MAP_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "map_doi_citationcount.csv")

# Function to fetch citation count asynchronously
async def fetch_citation_count(doi: str, session: ClientSession) -> int:
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi.strip()}?fields=citationCount"
    while True:
        try:
            async with session.get(url) as response:
                if response.status == 429:  # Too many requests
                    print("Rate limited. Waiting for 2 minutes...")
                    await asyncio.sleep(120)  # Wait for 2 minutes
                    continue

                if response.status != 200:
                    response_data = await response.json()
                    if "error" in response_data and "not found" in response_data["error"]:
                        return 0
                    print(f"Error fetching DOI {doi}: {response_data}")
                    return 0

                data = await response.json()
                return int(data["citationCount"])
        except Exception as e:
            print(f"Exception fetching DOI {doi}: {e}")
            return 0

# Asynchronous function to process the CSV and update citation counts
async def update_citation_counts(csv_path: str):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Ensure "citation_count" column exists
    if "citation_count" not in df.columns:
        df["citation_count"] = 0

    # Reverse the DataFrame for bottom-to-top processing
    df = df[::-1]

    # Create an aiohttp session
    async with aiohttp.ClientSession() as session:
        for index, row in df.iterrows():
            doi = row["doi"]

            # Skip rows with no DOI or that already have a citation count
            if pd.isna(doi) or (not pd.isna(row["citation_count"]) and int(row["citation_count"]) != 0):
                continue

            print(f"Processing DOI: {doi}")
            citation_count = await fetch_citation_count(doi, session)

            # Update the DataFrame
            df.at[index, "citation_count"] = citation_count

            # Save progress back to the CSV
            df.to_csv(csv_path, index=False)

            print(f"Updated DOI {doi} with citation count: {citation_count}")

# Main function to run the asyncio event loop
def main():
    asyncio.run(update_citation_counts(MAP_DIRECTORY))

if __name__ == "__main__":
    main()
