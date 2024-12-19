import pandas as pd
import spacy
from collections import Counter
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from langdetect import detect
import langdetect.lang_detect_exception
from tqdm import tqdm
import warnings
import multiprocessing as mp
from functools import partial
from spellchecker import SpellChecker
warnings.filterwarnings('ignore')

class LanguageAnalyzer:
    def __init__(self, n_processes=None):
        print("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm")
        self.n_processes = n_processes or mp.cpu_count()
        print("Initializing spell checker...")
        self.spell = SpellChecker()
        # Add common scientific/medical terms to avoid false positives
        self.spell.word_frequency.load_words([
            'covid', 'sars', 'cov', 'coronavirus', 'pandemic', 'epidemiology',
            'pathogen', 'asymptomatic', 'comorbidity', 'cytokine', 'genomic',
            'immunology', 'nosocomial', 'pathogenesis', 'prophylaxis', 'quarantine',
            'respiratory', 'transmission', 'vaccine', 'viral', 'virologic'
        ])
        
    def detect_language(self, text) -> Dict:
        """
        Enhanced language detection with detailed failure information.
        Returns dict with language and reason for the detection result.
        """
        if pd.isna(text):
            return {'lang': 'unknown', 'reason': 'null_value'}
        
        if not isinstance(text, str):
            return {'lang': 'unknown', 'reason': 'not_text'}
            
        text = text.strip()
        if len(text) == 0:
            return {'lang': 'unknown', 'reason': 'empty'}
            
        if len(text) < 10:
            return {'lang': 'unknown', 'reason': 'too_short'}
            
        try:
            lang = detect(text)
            return {'lang': lang, 'reason': 'langdetect_success'}
        except langdetect.lang_detect_exception.LangDetectException as e:
            try:
                doc = self.nlp(text[:1000])
                return {'lang': doc.lang_, 'reason': 'spacy_success'}
            except Exception as e:
                return {'lang': 'unknown', 'reason': f'both_failed:{str(e)}'}

    def check_spelling(self, text: str) -> List[Dict[str, str]]:
        """Check text for spelling errors/typos."""
        if not text:
            return []
        
        # Split text into words and check spelling
        words = text.lower().split()
        misspelled = self.spell.unknown(words)
        
        # Get corrections for misspelled words
        corrections = []
        for word in misspelled:
            # Get the most likely correction
            correction = self.spell.correction(word)
            if correction and correction != word:
                corrections.append({
                    'original': word,
                    'correction': correction
                })
        
        return corrections

    def check_text(self, text) -> Tuple[int, List[str], List[Dict[str, str]]]:
        """Check text for grammar errors and typos."""
        if pd.isna(text) or not isinstance(text, str):
            return 0, [], []
            
        doc = self.nlp(text)
        errors = []
        
        # Grammar checks
        for sent in doc.sents:
            has_subject = False
            has_verb = False
            for token in sent:
                if token.dep_ in ['nsubj', 'nsubjpass']:
                    has_subject = True
                if token.pos_ == 'VERB':
                    has_verb = True
            
            if not has_subject and len(list(sent)) > 3:
                errors.append('missing_subject')
            if not has_verb and len(list(sent)) > 3:
                errors.append('missing_verb')
                
            words = [token.text.lower() for token in sent if token.is_alpha]
            word_counts = Counter(words)
            repeated = [word for word, count in word_counts.items() 
                       if count > 1 and word not in ['the', 'a', 'an', 'and', 'or']]
            if repeated:
                errors.append('word_repetition')
        
        # Spell checking
        spelling_errors = self.check_spelling(text)
        if spelling_errors:
            errors.extend(['spelling_error'] * len(spelling_errors))
                
        return len(errors), errors, spelling_errors

    def analyze_document(self, row) -> Dict:
        """Analyze language and grammar of a document with enhanced tracking."""
        # Check for empty abstracts first
        abstract_text = row['abstract'] if isinstance(row['abstract'], str) else ''
        abstract_text = abstract_text.strip()
        abstract_status = 'present' if len(abstract_text) > 0 else 'empty'
        
        title_analysis = self.detect_language(row['title'])
        abstract_analysis = self.detect_language(row['abstract'])
        title_errors, title_types, title_spelling = self.check_text(row['title'])
        abstract_errors, abstract_types, abstract_spelling = self.check_text(row['abstract'])
        
        return {
            'cord_uid': row.get('cord_uid', ''),
            'relevance': row.get('relevance', ''),
            'title_language': title_analysis['lang'],
            'title_lang_reason': title_analysis['reason'],
            'abstract_language': abstract_analysis['lang'],
            'abstract_lang_reason': abstract_analysis['reason'],
            'abstract_status': abstract_status,
            'title': row['title'][:100] if isinstance(row['title'], str) else '',
            'abstract': row['abstract'][:100] if isinstance(row['abstract'], str) else '',
            'title_errors': title_errors,
            'title_error_types': title_types,
            'title_spelling_errors': title_spelling,
            'abstract_errors': abstract_errors,
            'abstract_error_types': abstract_types,
            'abstract_spelling_errors': abstract_spelling,
            'total_errors': title_errors + abstract_errors
        }

    def process_chunk(self, chunk):
        """Process a chunk of documents in parallel."""
        return [self.analyze_document(row) for _, row in chunk.iterrows()]

    def analyze_dataset(self, df: pd.DataFrame, qrels_analysis: bool = False) -> Dict:
        """
        Enhanced analysis of entire dataset including empty abstract detection.
        """
        if qrels_analysis:
            print("Analyzing relevant documents (including both relevance 1 and 2)...")
            relevant_df = df[df['relevance'] > 0]
            highest_relevance = (relevant_df.groupby('cord_uid')['relevance']
                               .max()
                               .reset_index())
            df = relevant_df.merge(highest_relevance, on=['cord_uid', 'relevance'])
            df = df.drop_duplicates(subset=['cord_uid'])
        else:
            print("Analyzing complete metadata (raw dataset)...")

        # Process documents
        chunk_size = max(1, len(df) // (self.n_processes * 4))
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        
        with mp.Pool(processes=self.n_processes) as pool:
            results = []
            with tqdm(total=len(df), desc="Processing documents") as pbar:
                for chunk_results in pool.imap(self.process_chunk, chunks):
                    results.extend(chunk_results)
                    pbar.update(len(chunk_results))
        
        results_df = pd.DataFrame(results)
        
        # Document completeness statistics
        completeness_stats = {
            'total_documents': len(results_df),
            'empty_abstracts': len(results_df[results_df['abstract_status'] == 'empty']),
            'documents_with_abstracts': len(results_df[results_df['abstract_status'] == 'present'])
        }
        
        # Filter for documents with abstracts for language analysis
        docs_with_abstracts = results_df[results_df['abstract_status'] == 'present']
        
        # Language statistics
        language_stats = {
            'title_languages': results_df['title_language'].value_counts().to_dict(),
            'abstract_languages': docs_with_abstracts['abstract_language'].value_counts().to_dict(),
            'document_languages': {
                'matching': len(docs_with_abstracts[
                    docs_with_abstracts['title_language'] == docs_with_abstracts['abstract_language']
                ]),
                'different': len(docs_with_abstracts[
                    docs_with_abstracts['title_language'] != docs_with_abstracts['abstract_language']
                ])
            },
            'unknown_abstracts': {
                'count': len(docs_with_abstracts[docs_with_abstracts['abstract_language'] == 'unknown']),
                'reasons': docs_with_abstracts[
                    docs_with_abstracts['abstract_language'] == 'unknown'
                ]['abstract_lang_reason'].value_counts().to_dict()
            }
        }
        
        # Grammar statistics
        grammar_stats = {
            'total_documents': len(docs_with_abstracts),
            'documents_with_errors': len(docs_with_abstracts[docs_with_abstracts['total_errors'] > 0]),
            'total_errors': docs_with_abstracts['total_errors'].sum(),
            'avg_errors_per_doc': docs_with_abstracts['total_errors'].mean(),
            'median_errors_per_doc': docs_with_abstracts['total_errors'].median(),
            'max_errors_per_doc': docs_with_abstracts['total_errors'].max(),
            'docs_with_title_errors': len(docs_with_abstracts[docs_with_abstracts['title_errors'] > 0]),
            'docs_with_abstract_errors': len(docs_with_abstracts[docs_with_abstracts['abstract_errors'] > 0]),
            'error_distribution': {
                'no_errors': len(docs_with_abstracts[docs_with_abstracts['total_errors'] == 0]),
                '1-2_errors': len(docs_with_abstracts[
                    (docs_with_abstracts['total_errors'] > 0) & 
                    (docs_with_abstracts['total_errors'] <= 2)
                ]),
                '3-5_errors': len(docs_with_abstracts[
                    (docs_with_abstracts['total_errors'] > 2) & 
                    (docs_with_abstracts['total_errors'] <= 5)
                ]),
                'more_than_5': len(docs_with_abstracts[docs_with_abstracts['total_errors'] > 5])
            }
        }
        
        # Error type frequencies
        title_types = [error for sublist in docs_with_abstracts['title_error_types'] for error in sublist]
        abstract_types = [error for sublist in docs_with_abstracts['abstract_error_types'] for error in sublist]
        
        # Count spelling errors
        title_spelling = sum(len(errors) for errors in docs_with_abstracts['title_spelling_errors'])
        abstract_spelling = sum(len(errors) for errors in docs_with_abstracts['abstract_spelling_errors'])
        
        grammar_stats['error_types'] = {
            'title': dict(Counter(title_types)),
            'abstract': dict(Counter(abstract_types)),
            'spelling': {
                'title': title_spelling,
                'abstract': abstract_spelling
            }
        }
        
        return {
            'completeness_stats': completeness_stats,
            'language_stats': language_stats,
            'grammar_stats': grammar_stats
        }

def print_analysis(stats: Dict, analysis_type: str):
    """Print enhanced formatted analysis results."""
    comp_stats = stats['completeness_stats']
    lang_stats = stats['language_stats']
    gram_stats = stats['grammar_stats']
    
    print(f"\n=== Document Completeness Analysis ({analysis_type}) ===")
    print(f"Total documents: {comp_stats['total_documents']}")
    print(f"Empty abstracts: {comp_stats['empty_abstracts']} ({comp_stats['empty_abstracts']/comp_stats['total_documents']*100:.1f}%)")
    print(f"Documents with abstracts: {comp_stats['documents_with_abstracts']} ({comp_stats['documents_with_abstracts']/comp_stats['total_documents']*100:.1f}%)")
    
    print(f"\n=== Language Analysis Results ({analysis_type}) ===")
    print("\nTitle Languages:")
    total_docs = comp_stats['total_documents']
    for lang, count in sorted(lang_stats['title_languages'].items(), key=lambda x: x[1], reverse=True):
        pct = count/total_docs*100
        print(f"{lang}: {count} documents ({pct:.1f}%)")
        
    print("\nAbstract Languages (Documents with Abstracts Only):")
    docs_with_abstracts = comp_stats['documents_with_abstracts']
    for lang, count in sorted(lang_stats['abstract_languages'].items(), key=lambda x: x[1], reverse=True):
        pct = count/docs_with_abstracts*100
        print(f"{lang}: {count} documents ({pct:.1f}%)")
    
    if lang_stats['unknown_abstracts']['count'] > 0:
        print("\nUnknown Abstract Language Analysis:")
        print(f"Total unknown: {lang_stats['unknown_abstracts']['count']}")
        print("Reasons:")
        for reason, count in lang_stats['unknown_abstracts']['reasons'].items():
            print(f"- {reason}: {count}")
        
    print("\nLanguage Consistency:")
    print(f"Documents with matching title/abstract languages: {lang_stats['document_languages']['matching']}")
    print(f"Documents with different title/abstract languages: {lang_stats['document_languages']['different']}")
    
    print(f"\n=== Grammar Analysis Results ({analysis_type}) ===")
    print(f"Documents analyzed (with abstracts): {gram_stats['total_documents']}")
    print(f"Documents with errors: {gram_stats['documents_with_errors']} ({gram_stats['documents_with_errors']/gram_stats['total_documents']*100:.1f}%)")
    print(f"Total errors found: {gram_stats['total_errors']}")
    print(f"Average errors per document: {gram_stats['avg_errors_per_doc']:.2f}")
    print(f"Median errors per document: {gram_stats['median_errors_per_doc']:.1f}")
    print(f"Maximum errors in a single document: {gram_stats['max_errors_per_doc']}")
    
    print("\nError Distribution:")
    for category, count in gram_stats['error_distribution'].items():
        pct = count/gram_stats['total_documents']*100
        print(f"{category}: {count} documents ({pct:.1f}%)")
    
    print("\nMost common error types:")
    print("\nIn titles:")
    for error, count in sorted(gram_stats['error_types']['title'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"- {error}: {count}")
    print("\nIn abstracts:")
    for error, count in sorted(gram_stats['error_types']['abstract'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"- {error}: {count}")
    
    print("\nSpelling Errors:")
    print(f"Title spelling errors: {gram_stats['error_types']['spelling']['title']}")
    print(f"Abstract spelling errors: {gram_stats['error_types']['spelling']['abstract']}")

def export_to_markdown(stats: Dict, output_file: str, analysis_type: str):
    """Create a detailed markdown report of the analysis."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Language and Grammar Analysis Report - {analysis_type}\n\n")
        
        # Document Completeness
        comp_stats = stats['completeness_stats']
        f.write("## Document Completeness\n\n")
        f.write(f"- Total Documents: {comp_stats['total_documents']:,}\n")
        f.write(f"- Empty Abstracts: {comp_stats['empty_abstracts']:,} ")
        f.write(f"({comp_stats['empty_abstracts']/comp_stats['total_documents']*100:.1f}%)\n")
        f.write(f"- Documents with Abstracts: {comp_stats['documents_with_abstracts']:,} ")
        f.write(f"({comp_stats['documents_with_abstracts']/comp_stats['total_documents']*100:.1f}%)\n\n")
        
        # Language Distribution
        f.write("## Language Distribution\n\n")
        f.write("### Title Languages\n\n")
        f.write("| Language | Count | Percentage |\n")
        f.write("|----------|--------|------------|\n")
        for lang, count in sorted(stats['language_stats']['title_languages'].items(), 
                                key=lambda x: x[1], 
                                reverse=True):
            pct = count/comp_stats['total_documents']*100
            f.write(f"| {lang.upper()} | {count:,} | {pct:.1f}% |\n")
        
        f.write("\n### Abstract Languages (Documents with Abstracts Only)\n\n")
        f.write("| Language | Count | Percentage |\n")
        f.write("|----------|--------|------------|\n")
        for lang, count in sorted(stats['language_stats']['abstract_languages'].items(), 
                                key=lambda x: x[1], 
                                reverse=True):
            pct = count/comp_stats['documents_with_abstracts']*100
            f.write(f"| {lang.upper()} | {count:,} | {pct:.1f}% |\n")
            
        # Unknown Language Analysis
        if stats['language_stats']['unknown_abstracts']['count'] > 0:
            f.write("\n### Unknown Language Analysis\n\n")
            f.write(f"Total Unknown: {stats['language_stats']['unknown_abstracts']['count']}\n\n")
            f.write("| Reason | Count |\n")
            f.write("|---------|--------|\n")
            for reason, count in stats['language_stats']['unknown_abstracts']['reasons'].items():
                f.write(f"| {reason} | {count:,} |\n")
        
        # Grammar Analysis
        gram_stats = stats['grammar_stats']
        f.write("\n## Grammar Analysis\n\n")
        f.write(f"- Documents Analyzed: {gram_stats['total_documents']:,}\n")
        f.write(f"- Documents with Errors: {gram_stats['documents_with_errors']:,} ")
        f.write(f"({gram_stats['documents_with_errors']/gram_stats['total_documents']*100:.1f}%)\n")
        f.write(f"- Total Errors Found: {gram_stats['total_errors']:,}\n")
        f.write(f"- Average Errors per Document: {gram_stats['avg_errors_per_doc']:.2f}\n")
        f.write(f"- Median Errors per Document: {gram_stats['median_errors_per_doc']:.1f}\n")
        f.write(f"- Maximum Errors in a Single Document: {gram_stats['max_errors_per_doc']}\n\n")
        
        # Error Distribution
        f.write("### Error Distribution\n\n")
        f.write("| Category | Count | Percentage |\n")
        f.write("|-----------|--------|------------|\n")
        for category, count in gram_stats['error_distribution'].items():
            pct = count/gram_stats['total_documents']*100
            f.write(f"| {category} | {count:,} | {pct:.1f}% |\n")
        
        # Error Types
        f.write("\n### Error Types\n\n")
        f.write("#### Title Errors\n\n")
        f.write("| Error Type | Count | Percentage |\n")
        f.write("|------------|--------|------------|\n")
        for error, count in sorted(gram_stats['error_types']['title'].items(), 
                                 key=lambda x: x[1], 
                                 reverse=True):
            pct = count/gram_stats['total_documents']*100
            f.write(f"| {error} | {count:,} | {pct:.1f}% |\n")
        
        f.write("\n#### Abstract Errors\n\n")
        f.write("| Error Type | Count | Percentage |\n")
        f.write("|------------|--------|------------|\n")
        for error, count in sorted(gram_stats['error_types']['abstract'].items(), 
                                 key=lambda x: x[1], 
                                 reverse=True):
            pct = count/gram_stats['total_documents']*100
            f.write(f"| {error} | {count:,} | {pct:.1f}% |\n")
        
        # Spelling Errors
        f.write("\n### Spelling Errors\n\n")
        f.write(f"- Title Spelling Errors: {gram_stats['error_types']['spelling']['title']:,}\n")
        f.write(f"- Abstract Spelling Errors: {gram_stats['error_types']['spelling']['abstract']:,}\n")

def main():
    # Initialize analyzer
    analyzer = LanguageAnalyzer()
    print(f"Using {analyzer.n_processes} processes for parallel processing...")
    
    # Load datasets
    print("Loading data...")
    metadata_df = pd.read_csv("data/2020-07-16/metadata.csv")
    qrels_df = pd.read_csv("data/qrel/qrels-covid_d5_j0.5-5.txt", 
                          sep=' ', 
                          header=None,
                          names=['topic', 'iteration', 'cord_uid', 'relevance'])
    
    # Part 1: Analyze qrels data
    print("\nProcessing qrels analysis...")
    merged_df = pd.merge(metadata_df, qrels_df, on='cord_uid', how='right')
    qrels_stats = analyzer.analyze_dataset(merged_df, qrels_analysis=True)
    print_analysis(qrels_stats, "Relevant Documents (Relevance 1 & 2)")
    export_to_markdown(qrels_stats, 'qrels_analysis_report.md', "Relevant Documents")
    
    # Part 2: Analyze pure metadata
    print("\nProcessing metadata-only analysis...")
    metadata_stats = analyzer.analyze_dataset(metadata_df, qrels_analysis=False)
    print_analysis(metadata_stats, "Complete Metadata (Raw Dataset)")
    export_to_markdown(metadata_stats, 'metadata_analysis_report.md', "Complete Dataset")
    
    # Save detailed results
    results = {
        'qrels_analysis': qrels_stats,
        'metadata_analysis': metadata_stats
    }
    
    pd.DataFrame([results]).to_json('enhanced_language_analysis.json', orient='records')
    print("\nDetailed results saved to:")
    print("- 'qrels_analysis_report.md'")
    print("- 'metadata_analysis_report.md'")
    print("- 'enhanced_language_analysis.json'")

if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()