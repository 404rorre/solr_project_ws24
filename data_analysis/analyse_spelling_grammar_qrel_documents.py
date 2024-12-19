import os
import logging
import pandas as pd
import numpy as np
from spellchecker import SpellChecker
from collections import defaultdict
from typing import Dict, Tuple, List
from functools import partial
import multiprocessing as mp
from tqdm import tqdm
import re
import warnings
from scipy.sparse import lil_matrix

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Extended medical/scientific terms
MEDICAL_TERMS = [
    'covid', 'sars', 'cov', 'coronavirus', 'pandemic', 'epidemiology',
    'pathogen', 'asymptomatic', 'comorbidity', 'cytokine', 'genomic',
    'immunology', 'nosocomial', 'pathogenesis', 'prophylaxis', 'quarantine',
    'respiratory', 'transmission', 'vaccine', 'viral', 'virologic',
    'clinical', 'diagnosis', 'therapeutic', 'protocol', 'syndrome',
    'symptoms', 'infection', 'infectious', 'mortality', 'morbidity',
    'antibody', 'antibodies', 'immune', 'immunization', 'prevention',
    'analysis', 'study', 'research', 'methodology', 'hypothesis',
    'data', 'results', 'conclusion', 'findings', 'evidence',
    'statistical', 'significant', 'population', 'sample', 'cohort',
    'et', 'al', 'ie', 'eg', 'vs', 'etc'
]

#######################
# GLOBAL INITIALIZATION
#######################

global_spell = SpellChecker()
global_spell.word_frequency.load_words(MEDICAL_TERMS)
known_words = set(global_spell.word_frequency.words())

####################
# HELPER FUNCTIONS #
####################

def is_likely_acronym(word: str) -> bool:
    return (word.isupper() and len(word) >= 2) or (bool(re.match(r'^[A-Z0-9-]+$', word)) and len(word) >= 2)

def is_likely_number_or_id(word: str) -> bool:
    return bool(re.search(r'\d', word)) or bool(re.match(r'^[A-Za-z0-9-]+$', word)) or '-' in word

def clean_and_split_text(text: str) -> List[str]:
    if pd.isnull(text):
        return []
    words = text.lower().split()
    words = [w.strip('.,;:()"\'') for w in words if w]
    return words

##########################
# MULTIPROCESSING TARGET #
##########################

def process_text_chunk(texts_chunk: pd.Series) -> Dict[str, int]:
    """Count word frequencies in a chunk of documents."""
    word_freq = defaultdict(int)
    for text in texts_chunk:
        for word in clean_and_split_text(text):
            word_freq[word] += 1
    return dict(word_freq)

def process_doc_chunk_for_matrix(doc_chunk: pd.DataFrame, word_to_id: Dict[str, int]) -> Tuple[List[int], List[int], List[int]]:
    """
    Process a chunk of documents and return their (row, col, data) for a sparse matrix.
    """
    rows = []
    cols = []
    data = []
    for i, (_, doc) in enumerate(doc_chunk.iterrows()):
        # title
        for w in clean_and_split_text(doc['title']):
            if w in word_to_id:
                rows.append(i)
                cols.append(word_to_id[w])
                data.append(1)
        # abstract
        for w in clean_and_split_text(doc['abstract']):
            if w in word_to_id:
                rows.append(i)
                cols.append(word_to_id[w])
                data.append(1)
    return rows, cols, data

def check_spelling_for_chunk(words_chunk: List[str]) -> Dict[str, bool]:
    """
    Check spelling for a chunk of words using global spell checker and known words.
    Returns: word -> is_error (bool).
    """
    result = {}
    for word in words_chunk:
        if is_likely_acronym(word) or is_likely_number_or_id(word) or len(word) < 3:
            result[word] = False
            continue

        if word in known_words:
            # Word is known correct
            result[word] = False
        else:
            # Word not known, attempt correction
            correction = global_spell.correction(word)
            if correction and correction != word:
                result[word] = True
            else:
                result[word] = False
    return result

###################
# MAIN FUNCTIONS  #
###################

def build_vocabulary(texts: pd.Series, n_processes: int) -> Dict[str, int]:
    """
    Builds the vocabulary (word -> id) using multiprocessing.
    """
    chunks = np.array_split(texts, n_processes)
    logging.info(f"Number of chunks for vocabulary: {len(chunks)}")

    with mp.Pool(n_processes) as pool:
        chunk_results = list(tqdm(
            pool.imap(process_text_chunk, chunks, chunksize=64),
            total=len(chunks),
            desc="Building vocabulary"
        ))

    total_freq = defaultdict(int)
    for freq_dict in chunk_results:
        for w, f in freq_dict.items():
            total_freq[w] += f

    all_words = sorted(total_freq.keys())
    word_to_id = {w: i for i, w in enumerate(all_words)}
    return word_to_id

def build_document_term_matrix(df: pd.DataFrame, word_to_id: Dict[str, int], n_processes: int):
    """
    Build a sparse document-term matrix for the given DataFrame.
    """
    doc_chunks = np.array_split(df, n_processes)
    logging.info(f"Number of doc chunks: {len(doc_chunks)}")

    partial_func = partial(process_doc_chunk_for_matrix, word_to_id=word_to_id)

    with mp.Pool(n_processes) as pool:
        chunk_results = list(tqdm(
            pool.imap(partial_func, doc_chunks, chunksize=64),
            total=len(doc_chunks),
            desc="Building DTM"
        ))

    row_offsets = 0
    rows_list, cols_list, data_list = [], [], []
    for chunk_idx, (r, c, d) in enumerate(chunk_results):
        adjusted_r = [x + row_offsets for x in r]
        rows_list.extend(adjusted_r)
        cols_list.extend(c)
        data_list.extend(d)
        row_offsets += len(doc_chunks[chunk_idx])

    n_docs = len(df)
    n_words = len(word_to_id)
    dtm = lil_matrix((n_docs, n_words), dtype=int)
    for r, c, val in zip(rows_list, cols_list, data_list):
        dtm[r, c] += val
    return dtm.tocsr()

def spell_check_vocabulary(word_to_id: Dict[str, int], n_processes: int) -> np.ndarray:
    """
    Spell check each word in the vocabulary and return a binary vector 
    indicating error (1) or correct (0).
    """
    words = list(word_to_id.keys())
    word_chunks = np.array_split(words, n_processes)
    logging.info(f"Number of word chunks for spell checking: {len(word_chunks)}")

    with mp.Pool(n_processes) as pool:
        chunk_results = list(tqdm(
            pool.imap(check_spelling_for_chunk, word_chunks, chunksize=64),
            total=len(word_chunks),
            desc="Spell Checking Vocabulary"
        ))

    is_error_dict = {}
    for cr in chunk_results:
        is_error_dict.update(cr)

    is_error_vector = np.zeros(len(word_to_id), dtype=int)
    for w, idx in word_to_id.items():
        is_error_vector[idx] = 1 if is_error_dict[w] else 0

    return is_error_vector

def analyze_dataset(metadata_df: pd.DataFrame, qrels_df: pd.DataFrame, n_processes: int) -> Tuple[pd.DataFrame, Dict[str, int], np.ndarray, 'csr_matrix']:
    """
    Analyze the dataset using the bag-of-words approach and spell-check vector.
    """
    unique_docs = qrels_df['cord_uid'].unique()
    metadata_filtered = metadata_df[metadata_df['cord_uid'].isin(unique_docs)].copy()
    highest_relevance = qrels_df.groupby(['cord_uid', 'topic'])['relevance'].max().reset_index()
    merged_df = pd.merge(metadata_filtered, highest_relevance, on='cord_uid')
    merged_df = merged_df.drop_duplicates(subset=['title', 'abstract']).reset_index(drop=True)

    all_texts = pd.concat([merged_df['title'], merged_df['abstract']], ignore_index=True)
    word_to_id = build_vocabulary(all_texts, n_processes)
    dtm = build_document_term_matrix(merged_df, word_to_id, n_processes)
    is_error_vector = spell_check_vocabulary(word_to_id, n_processes)
    doc_errors = dtm.dot(is_error_vector)
    merged_df['total_errors'] = doc_errors
    return merged_df, word_to_id, is_error_vector, dtm

def print_stats(results_df: pd.DataFrame, word_to_id: Dict[str, int], is_error_vector: np.ndarray, dtm):
    total_docs = len(results_df)
    docs_with_errors = (results_df['total_errors'] > 0).sum()
    avg_errors = results_df['total_errors'].mean()
    print("\n=== Enhanced Analysis Results ===")
    print(f"Total Documents Analyzed: {total_docs}")
    print(f"Documents with Errors: {docs_with_errors} ({docs_with_errors/total_docs:.2%})")
    print(f"Average Errors per Document: {avg_errors:.2f}")

    error_word_ids = np.where(is_error_vector == 1)[0]
    if len(error_word_ids) > 0:
        word_counts = np.array(dtm[:, error_word_ids].sum(axis=0)).flatten()
        error_words = [w for w, i in word_to_id.items() if is_error_vector[i] == 1]
        error_word_counts = list(zip(error_words, word_counts))
        error_word_counts.sort(key=lambda x: x[1], reverse=True)

        print("\nTop 10 Most Frequent Error Words:")
        for w, c in error_word_counts[:10]:
            print(f"'{w}': {int(c)} occurrences")
    else:
        print("\nNo spelling errors identified in the vocabulary.")

def main():
    # Optionally specify the start method if needed:
    # mp.set_start_method('spawn')  # On Windows if required
    # mp.set_start_method('fork')   # On Unix (usually default)

    metadata_path = "data/2020-07-16/metadata.csv"
    qrels_path = "data/qrel/qrels-covid_d5_j0.5-5.txt"

    if not os.path.exists(metadata_path):
        logging.error(f"Metadata file not found at '{metadata_path}'")
        return
    if not os.path.exists(qrels_path):
        logging.error(f"Qrels file not found at '{qrels_path}'")
        return

    logging.info("Loading data...")
    metadata_df = pd.read_csv(metadata_path)
    qrels_df = pd.read_csv(qrels_path, sep=' ', header=None, names=['topic', 'iteration', 'cord_uid', 'relevance'])

    n_processes = max(2, mp.cpu_count() - 1)  # Ensure at least 2 processes
    logging.info(f"Using {n_processes} processes for parallel work.")

    results_df, word_to_id, is_error_vector, dtm = analyze_dataset(metadata_df, qrels_df, n_processes)
    print_stats(results_df, word_to_id, is_error_vector, dtm)

    output_path = 'bow_spell_check_results.csv'
    results_df.to_csv(output_path, index=False)
    logging.info(f"Detailed results saved to '{output_path}'")

if __name__ == "__main__":
    main()
