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
warnings.filterwarnings('ignore')

class EnhancedLanguageAnalyzer:
    def __init__(self, n_processes=None):
        print("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm")
        self.n_processes = n_processes or mp.cpu_count()
        
    def detect_language(self, text) -> Dict:
        """Enhanced language detection with detailed failure information."""
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
            # First attempt with langdetect
            lang = detect(text)
            return {'lang': lang, 'reason': 'langdetect_success'}
        except langdetect.lang_detect_exception.LangDetectException as e:
            try:
                # Backup attempt with spaCy
                doc = self.nlp(text[:1000])
                return {'lang': doc.lang_, 'reason': 'spacy_success'}
            except Exception as e:
                return {'lang': 'unknown', 'reason': f'both_failed:{str(e)}'}

    def check_text(self, text) -> Tuple[int, List[str]]:
        """Check text for grammatical errors and structural issues."""
        if pd.isna(text) or not isinstance(text, str):
            return 0, []
            
        doc = self.nlp(text)
        errors = []
        
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
                
        return len(errors), errors

    def analyze_document(self, row) -> Dict:
        """Analyze language and grammar of a document with detailed language detection info."""
        # Check for empty abstracts first
        abstract_text = row['abstract'] if isinstance(row['abstract'], str) else ''
        abstract_text = abstract_text.strip()
        abstract_status = 'present' if len(abstract_text) > 0 else 'empty'
        
        title_analysis = self.detect_language(row['title'])
        abstract_analysis = self.detect_language(row['abstract'])
        title_errors, title_types = self.check_text(row['title'])
        abstract_errors, abstract_types = self.check_text(row['abstract'])
        
        return {
            'cord_uid': row['cord_uid'],
            'relevance': row['relevance'],
            'title_language': title_analysis['lang'],
            'title_lang_reason': title_analysis['reason'],
            'abstract_language': abstract_analysis['lang'],
            'abstract_lang_reason': abstract_analysis['reason'],
            'abstract_status': abstract_status,
            'title': row['title'][:100] if isinstance(row['title'], str) else '',
            'abstract': row['abstract'][:100] if isinstance(row['abstract'], str) else '',
            'title_errors': title_errors,
            'title_error_types': title_types,
            'abstract_errors': abstract_errors,
            'abstract_error_types': abstract_types,
            'total_errors': title_errors + abstract_errors
        }

    def process_chunk(self, chunk):
        """Process a chunk of documents in parallel."""
        return [self.analyze_document(row) for _, row in chunk.iterrows()]

    def analyze_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze the entire dataset using parallel processing."""
        print("Preparing documents for analysis...")
        chunk_size = max(1, len(df) // (self.n_processes * 4))
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        print(f"Created {len(chunks)} chunks of size {chunk_size}")
        
        with mp.Pool(processes=self.n_processes) as pool:
            results = []
            with tqdm(total=len(df), desc="Processing documents", position=0, leave=True) as pbar:
                for chunk_results in pool.imap(self.process_chunk, chunks):
                    results.extend(chunk_results)
                    pbar.update(len(chunk_results))
        
        return pd.DataFrame(results)

def analyze_document_completeness(results_df: pd.DataFrame) -> None:
    """Analyze and print information about document completeness."""
    print("\n=== Document Completeness Analysis ===")
    
    total_docs = len(results_df)
    empty_abstracts = results_df[results_df['abstract_status'] == 'empty']
    empty_abstract_count = len(empty_abstracts)
    
    print(f"\nTotal Documents: {total_docs}")
    print(f"Documents with Empty Abstracts: {empty_abstract_count} ({empty_abstract_count/total_docs*100:.1f}%)")
    
    # Analyze language detection failures for documents with abstracts
    docs_with_abstracts = results_df[results_df['abstract_status'] == 'present']
    unknown_abstracts = docs_with_abstracts[docs_with_abstracts['abstract_language'] == 'unknown']
    
    print("\nLanguage Detection Analysis (Documents with Non-Empty Abstracts):")
    print(f"Total Documents with Abstracts: {len(docs_with_abstracts)}")
    print(f"Failed Language Detection: {len(unknown_abstracts)} ({len(unknown_abstracts)/len(docs_with_abstracts)*100:.1f}%)")
    
    if len(unknown_abstracts) > 0:
        print("\nReasons for Language Detection Failure:")
        reason_counts = unknown_abstracts['abstract_lang_reason'].value_counts()
        for reason, count in reason_counts.items():
            print(f"- {reason}: {count} documents")

def analyze_by_language_and_relevance(results_df: pd.DataFrame) -> Dict:
    """Generate comprehensive analysis of languages, relevance, and errors."""
    # Only analyze documents with present abstracts
    results_df = results_df[results_df['abstract_status'] == 'present']
    
    lang_rel_stats = {}
    for lang in results_df['abstract_language'].unique():
        lang_docs = results_df[results_df['abstract_language'] == lang]
        rel_1_count = len(lang_docs[lang_docs['relevance'] == 1])
        rel_2_count = len(lang_docs[lang_docs['relevance'] == 2])
        
        avg_errors = lang_docs['total_errors'].mean()
        error_types = {
            'title': Counter([err for errs in lang_docs['title_error_types'] for err in errs]),
            'abstract': Counter([err for errs in lang_docs['abstract_error_types'] for err in errs])
        }
        
        lang_rel_stats[lang] = {
            'total_documents': len(lang_docs),
            'relevance_1_docs': rel_1_count,
            'relevance_2_docs': rel_2_count,
            'average_errors': avg_errors,
            'documents_with_errors': len(lang_docs[lang_docs['total_errors'] > 0]),
            'error_types': error_types
        }
    
    return lang_rel_stats

def print_enhanced_analysis(stats: Dict):
    """Print formatted analysis results."""
    print("\n=== Enhanced Language, Relevance, and Grammar Analysis ===")
    
    sorted_langs = sorted(stats.items(), 
                         key=lambda x: x[1]['total_documents'], 
                         reverse=True)
    
    for lang, data in sorted_langs:
        total_docs = data['total_documents']
        if total_docs == 0:
            continue
            
        print(f"\n\nLanguage: {lang.upper()}")
        print("=" * 50)
        print(f"Total Documents: {total_docs}")
        print(f"Relevance Distribution:")
        print(f"  - Relevance 1: {data['relevance_1_docs']} ({data['relevance_1_docs']/total_docs*100:.1f}%)")
        print(f"  - Relevance 2: {data['relevance_2_docs']} ({data['relevance_2_docs']/total_docs*100:.1f}%)")
        
        print(f"\nError Analysis:")
        print(f"  - Average errors per document: {data['average_errors']:.2f}")
        print(f"  - Documents with errors: {data['documents_with_errors']} ({data['documents_with_errors']/total_docs*100:.1f}%)")
        
        if data['error_types']['title'] or data['error_types']['abstract']:
            print("\nMost Common Error Types:")
            print("  In Titles:")
            for error, count in sorted(data['error_types']['title'].items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:3]:
                print(f"    - {error}: {count}")
            
            print("  In Abstracts:")
            for error, count in sorted(data['error_types']['abstract'].items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:3]:
                print(f"    - {error}: {count}")

def export_to_markdown(stats: Dict, output_file: str):
    """Create a detailed markdown report of the analysis."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Language, Relevance, and Grammar Analysis Report\n\n")
        f.write("## Overview\n\n")
        
        # Calculate overall statistics
        total_docs = sum(data['total_documents'] for data in stats.values())
        total_rel1 = sum(data['relevance_1_docs'] for data in stats.values())
        total_rel2 = sum(data['relevance_2_docs'] for data in stats.values())
        
        f.write(f"- Total Documents Analyzed: {total_docs:,}\n")
        f.write(f"- Documents with Relevance 1: {total_rel1:,}\n")
        f.write(f"- Documents with Relevance 2: {total_rel2:,}\n\n")
        
        # Create summary table
        f.write("## Language Distribution Summary\n\n")
        f.write("| Language | Total Docs | Rel 1 | Rel 2 | Avg Errors | Docs with Errors |\n")
        f.write("|----------|------------|--------|--------|------------|----------------|\n")
        
        sorted_langs = sorted(stats.items(), 
                            key=lambda x: x[1]['total_documents'], 
                            reverse=True)
        
        for lang, data in sorted_langs:
            if data['total_documents'] == 0:
                continue
                
            total = data['total_documents']
            f.write(f"| {lang.upper()} | {total:,} | ")
            f.write(f"{data['relevance_1_docs']:,} ({data['relevance_1_docs']/total*100:.1f}%) | ")
            f.write(f"{data['relevance_2_docs']:,} ({data['relevance_2_docs']/total*100:.1f}%) | ")
            f.write(f"{data['average_errors']:.2f} | ")
            f.write(f"{data['documents_with_errors']:,} ({data['documents_with_errors']/total*100:.1f}%) |\n")
        
        # Detailed analysis by language
        f.write("\n## Detailed Analysis by Language\n\n")
        
        for lang, data in sorted_langs:
            if data['total_documents'] == 0:
                continue
                
            f.write(f"### {lang.upper()}\n\n")
            total = data['total_documents']
            
            # Document statistics
            f.write("#### Document Statistics\n\n")
            f.write(f"- Total Documents: {total:,}\n")
            f.write(f"- Relevance 1: {data['relevance_1_docs']:,} ({data['relevance_1_docs']/total*100:.1f}%)\n")
            f.write(f"- Relevance 2: {data['relevance_2_docs']:,} ({data['relevance_2_docs']/total*100:.1f}%)\n\n")
            
            # Error analysis
            f.write("#### Error Analysis\n\n")
            f.write(f"- Average Errors per Document: {data['average_errors']:.2f}\n")
            f.write(f"- Documents with Errors: {data['documents_with_errors']:,} ")
            f.write(f"({data['documents_with_errors']/total*100:.1f}%)\n\n")
            
            # Error types tables
            if data['error_types']['title'] or data['error_types']['abstract']:
                f.write("#### Most Common Error Types\n\n")
                
                if data['error_types']['title']:
                    f.write("**Title Errors**\n\n")
                    f.write("| Error Type | Count | Percentage |\n")
                    f.write("|------------|--------|------------|\n")
                    for error, count in sorted(data['error_types']['title'].items(), 
                                             key=lambda x: x[1], 
                                             reverse=True):
                        f.write(f"| {error} | {count:,} | {count/total*100:.1f}% |\n")
                    f.write("\n")
                
                if data['error_types']['abstract']:
                    f.write("**Abstract Errors**\n\n")
                    f.write("| Error Type | Count | Percentage |\n")
                    f.write("|------------|--------|------------|\n")
                    for error, count in sorted(data['error_types']['abstract'].items(), 
                                             key=lambda x: x[1], 
                                             reverse=True):
                        f.write(f"| {error} | {count:,} | {count/total*100:.1f}% |\n")
                    f.write("\n")
            
            f.write("\n---\n\n")  # Separator
def export_detailed_results(results_df: pd.DataFrame, filename: str):
    """Export detailed results including empty abstract information."""
    analysis_results = {
        'total_documents': len(results_df),
        'empty_abstracts': len(results_df[results_df['abstract_status'] == 'empty']),
        'documents_with_abstracts': len(results_df[results_df['abstract_status'] == 'present']),
        'language_distribution': results_df[results_df['abstract_status'] == 'present']['abstract_language'].value_counts().to_dict(),
        'unknown_language_reasons': results_df[
            (results_df['abstract_status'] == 'present') & 
            (results_df['abstract_language'] == 'unknown')
        ]['abstract_lang_reason'].value_counts().to_dict()
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Detailed Analysis Results\n\n")
        
        f.write("## Document Completeness\n")
        f.write(f"- Total Documents: {analysis_results['total_documents']}\n")
        f.write(f"- Empty Abstracts: {analysis_results['empty_abstracts']}\n")
        f.write(f"- Documents with Abstracts: {analysis_results['documents_with_abstracts']}\n\n")
        
        f.write("## Language Distribution (Documents with Abstracts)\n")
        for lang, count in sorted(analysis_results['language_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = count/analysis_results['documents_with_abstracts']*100
            f.write(f"- {lang}: {count} ({percentage:.1f}%)\n")
        
        if analysis_results['unknown_language_reasons']:
            f.write("\n## Unknown Language Analysis\n")
            for reason, count in analysis_results['unknown_language_reasons'].items():
                f.write(f"- {reason}: {count}\n")

def main():
    # Initialize analyzer
    analyzer = EnhancedLanguageAnalyzer()
    print(f"Using {analyzer.n_processes} processes for parallel processing...")
    
    # Load and prepare dataset
    print("Loading data...")
    metadata_df = pd.read_csv("data/2020-07-16/metadata.csv")
    qrels_df = pd.read_csv("data/qrel/qrels-covid_d5_j0.5-5.txt", 
                          sep=' ', 
                          header=None,
                          names=['topic', 'iteration', 'cord_uid', 'relevance'])
    
    # Merge and handle duplicates
    print("Preparing merged dataset...")
    merged_df = pd.merge(metadata_df, qrels_df, on='cord_uid', how='right')
    relevant_df = merged_df[merged_df['relevance'] > 0]
    # Keep highest relevance per document
    highest_relevance = (relevant_df.groupby('cord_uid')['relevance']
                        .max()
                        .reset_index())
    final_df = relevant_df.merge(highest_relevance, on=['cord_uid', 'relevance'])
    final_df = final_df.drop_duplicates(subset=['cord_uid'])
    
    # Analyze dataset
    print("\nAnalyzing documents...")
    results_df = analyzer.analyze_dataset(final_df)
    
    # Analyze document completeness
    analyze_document_completeness(results_df)
    
    # Generate and print language analysis
    analysis = analyze_by_language_and_relevance(results_df)
    print_enhanced_analysis(analysis)
    
    # Export to markdown
    export_to_markdown(analysis, 'language_analysis_report.md')
    print("\nLanguage analysis report saved to 'language_analysis_report.md'")
    
    # Export detailed results
    export_detailed_results(results_df, 'detailed_analysis_report.md')
    print("Detailed analysis report saved to 'detailed_analysis_report.md'")
    
    # Save full results
    results_df.to_json('enhanced_language_analysis.json', orient='records')
    print("Complete analysis results saved to 'enhanced_language_analysis.json'")

if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()