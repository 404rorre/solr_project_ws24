import pandas as pd
from pathlib import Path

def export_missing_relevant_docs():
    """
    Export relevant documents (relevance > 0) with missing metadata into three separate files:
    - missing_titles.csv: Documents missing only titles
    - missing_abstracts.csv: Documents missing only abstracts 
    - missing_both.csv: Documents missing both title and abstract
    """
    # Load data
    print("Loading data...")
    metadata_df = pd.read_csv("data/2020-07-16/metadata.csv")
    qrels_df = pd.read_csv("data/qrel/qrels-covid_d5_j0.5-5.txt", 
                          sep=' ', 
                          header=None,
                          names=['topic', 'iteration', 'cord_uid', 'relevance'])

    # Merge datasets
    print("Merging datasets...")
    merged_df = pd.merge(metadata_df, qrels_df, on='cord_uid', how='right')
    
    # Filter for relevant documents only
    relevant_docs = merged_df[merged_df['relevance'] > 0]

    # Identify missing data
    missing_title = relevant_docs[relevant_docs['title'].isna()]
    missing_abstract = relevant_docs[relevant_docs['abstract'].isna()]
    missing_both = relevant_docs[relevant_docs['title'].isna() & relevant_docs['abstract'].isna()]

    # Columns to export
    cols_to_export = ['cord_uid', 'title', 'abstract', 'authors', 'journal', 
                      'publish_time', 'url', 'topic', 'relevance']

    # Export files
    print("Exporting documents...")
    missing_title[cols_to_export].to_csv("data_manipulation/missing_titles.csv", index=False)
    missing_abstract[cols_to_export].to_csv("data_manipulation/missing_abstracts.csv", index=False)
    missing_both[cols_to_export].to_csv("data_manipulation/missing_both.csv", index=False)

    # Print summary
    print(f"\nExport complete:")
    print(f"Documents missing titles: {len(missing_title)}")
    print(f"Documents missing abstracts: {len(missing_abstract)}")
    print(f"Documents missing both: {len(missing_both)}")

if __name__ == "__main__":
    export_missing_relevant_docs()