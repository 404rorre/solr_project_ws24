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
import xml.etree.ElementTree as ET
warnings.filterwarnings('ignore')

class TopicAnalyzer:
    def __init__(self, n_processes=None):
        print("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm")
        self.n_processes = n_processes or mp.cpu_count()
        
    def detect_language(self, text) -> str:
        """
        Detect language of text using both spacy and langdetect.
        Returns ISO language code.
        """
        if pd.isna(text) or not isinstance(text, str) or len(text.strip()) < 10:
            return 'unknown'
            
        try:
            lang = detect(text)
            return lang
        except (langdetect.lang_detect_exception.LangDetectException, Exception):
            try:
                doc = self.nlp(text[:1000])
                return doc.lang_
            except:
                return 'unknown'

    def check_text(self, text) -> Tuple[int, List[str]]:
        """Check text for grammar errors."""
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

    def analyze_topic(self, topic_elem) -> Dict:
        """Analyze language and grammar of a topic."""
        query = topic_elem.find('query').text
        question = topic_elem.find('question').text
        narrative = topic_elem.find('narrative').text
        
        query_lang = self.detect_language(query)
        question_lang = self.detect_language(question)
        narrative_lang = self.detect_language(narrative)
        
        query_errors, query_types = self.check_text(query)
        question_errors, question_types = self.check_text(question)
        narrative_errors, narrative_types = self.check_text(narrative)
        
        return {
            'topic_number': topic_elem.get('number'),
            'query_language': query_lang,
            'question_language': question_lang,
            'narrative_language': narrative_lang,
            'query_errors': query_errors,
            'query_error_types': query_types,
            'question_errors': question_errors,
            'question_error_types': question_types,
            'narrative_errors': narrative_errors,
            'narrative_error_types': narrative_types,
            'total_errors': query_errors + question_errors + narrative_errors
        }

    def process_chunk(self, topics):
        """Process a chunk of topics in parallel."""
        return [self.analyze_topic(topic) for topic in topics]

    def analyze_topics_file(self, xml_file: str) -> Dict:
        """Analyze topics file for language and grammar using parallel processing."""
        print(f"Parsing XML file: {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        topics = root.findall('.//topic')
        
        # Split topics into chunks for parallel processing
        chunk_size = len(topics) // (self.n_processes * 4)  # 4 chunks per process for better load balancing
        chunk_size = max(1, chunk_size)  # Ensure at least 1 topic per chunk
        chunks = [topics[i:i + chunk_size] for i in range(0, len(topics), chunk_size)]
        
        # Create a pool of workers
        results = []
        with mp.Pool(processes=self.n_processes) as pool:
            # Process chunks in parallel with progress bar
            with tqdm(total=len(topics), desc="Processing topics") as pbar:
                for chunk_results in pool.imap(self.process_chunk, chunks):
                    results.extend(chunk_results)
                    pbar.update(len(chunk_results))
        
        results_df = pd.DataFrame(results)
        
        # Language statistics
        language_stats = {
            'query_languages': results_df['query_language'].value_counts().to_dict(),
            'question_languages': results_df['question_language'].value_counts().to_dict(),
            'narrative_languages': results_df['narrative_language'].value_counts().to_dict(),
            'section_languages': {
                'matching': len(results_df[
                    (results_df['query_language'] == results_df['question_language']) &
                    (results_df['question_language'] == results_df['narrative_language'])
                ]),
                'different': len(results_df[
                    (results_df['query_language'] != results_df['question_language']) |
                    (results_df['question_language'] != results_df['narrative_language'])
                ])
            }
        }
        
        # Grammar statistics
        total_topics = len(topics)
        grammar_stats = {
            'total_topics': total_topics,
            'topics_with_errors': len(results_df[results_df['total_errors'] > 0]),
            'total_errors': results_df['total_errors'].sum(),
            'avg_errors_per_topic': results_df['total_errors'].mean(),
            'median_errors_per_topic': results_df['total_errors'].median(),
            'max_errors_per_topic': results_df['total_errors'].max(),
            'topics_with_query_errors': len(results_df[results_df['query_errors'] > 0]),
            'topics_with_question_errors': len(results_df[results_df['question_errors'] > 0]),
            'topics_with_narrative_errors': len(results_df[results_df['narrative_errors'] > 0]),
            'error_distribution': {
                'no_errors': len(results_df[results_df['total_errors'] == 0]),
                '1-2_errors': len(results_df[(results_df['total_errors'] > 0) & (results_df['total_errors'] <= 2)]),
                '3-5_errors': len(results_df[(results_df['total_errors'] > 2) & (results_df['total_errors'] <= 5)]),
                'more_than_5': len(results_df[results_df['total_errors'] > 5])
            }
        }
        
        # Error type frequencies
        query_types = [error for sublist in results_df['query_error_types'] for error in sublist]
        question_types = [error for sublist in results_df['question_error_types'] for error in sublist]
        narrative_types = [error for sublist in results_df['narrative_error_types'] for error in sublist]
        
        grammar_stats['error_types'] = {
            'query': dict(Counter(query_types)),
            'question': dict(Counter(question_types)),
            'narrative': dict(Counter(narrative_types))
        }
        
        return {'language_stats': language_stats, 'grammar_stats': grammar_stats}

def print_analysis(stats: Dict, analysis_type: str):
    """Print formatted analysis results."""
    lang_stats = stats['language_stats']
    gram_stats = stats['grammar_stats']
    
    print(f"\n=== Language Analysis Results ({analysis_type}) ===")
    print("\nQuery Languages:")
    for lang, count in sorted(lang_stats['query_languages'].items(), key=lambda x: x[1], reverse=True):
        pct = count/gram_stats['total_topics']*100
        print(f"{lang}: {count} topics ({pct:.1f}%)")
        
    print("\nQuestion Languages:")
    for lang, count in sorted(lang_stats['question_languages'].items(), key=lambda x: x[1], reverse=True):
        pct = count/gram_stats['total_topics']*100
        print(f"{lang}: {count} topics ({pct:.1f}%)")
        
    print("\nNarrative Languages:")
    for lang, count in sorted(lang_stats['narrative_languages'].items(), key=lambda x: x[1], reverse=True):
        pct = count/gram_stats['total_topics']*100
        print(f"{lang}: {count} topics ({pct:.1f}%)")
        
    print("\nLanguage Consistency:")
    print(f"Topics with matching languages across sections: {lang_stats['section_languages']['matching']}")
    print(f"Topics with different languages across sections: {lang_stats['section_languages']['different']}")
    
    print(f"\n=== Grammar Analysis Results ({analysis_type}) ===")
    print(f"Total topics analyzed: {gram_stats['total_topics']}")
    print(f"Topics with errors: {gram_stats['topics_with_errors']} ({gram_stats['topics_with_errors']/gram_stats['total_topics']*100:.1f}%)")
    print(f"Total errors found: {gram_stats['total_errors']}")
    print(f"Average errors per topic: {gram_stats['avg_errors_per_topic']:.2f}")
    print(f"Median errors per topic: {gram_stats['median_errors_per_topic']:.1f}")
    print(f"Maximum errors in a single topic: {gram_stats['max_errors_per_topic']}")
    
    print("\nError Distribution:")
    for category, count in gram_stats['error_distribution'].items():
        pct = count/gram_stats['total_topics']*100
        print(f"{category}: {count} topics ({pct:.1f}%)")
    
    print("\nMost common error types:")
    print("\nIn queries:")
    for error, count in sorted(gram_stats['error_types']['query'].items(), key=lambda x: x[1], reverse=True):
        print(f"- {error}: {count}")
    print("\nIn questions:")
    for error, count in sorted(gram_stats['error_types']['question'].items(), key=lambda x: x[1], reverse=True):
        print(f"- {error}: {count}")
    print("\nIn narratives:")
    for error, count in sorted(gram_stats['error_types']['narrative'].items(), key=lambda x: x[1], reverse=True):
        print(f"- {error}: {count}")

def main():
    # Initialize analyzer with desired number of processes (default: number of CPU cores)
    analyzer = TopicAnalyzer()
    
    print(f"Using {analyzer.n_processes} processes for parallel processing...")
    
    # Analyze topics file
    stats = analyzer.analyze_topics_file("data/topics/topics-rnd5.xml")
    print_analysis(stats, "Topics Analysis")
    
    # Save detailed results
    pd.DataFrame([stats]).to_json('topic_language_and_grammar_analysis.json')
    print("\nDetailed results saved to 'topic_language_and_grammar_analysis.json'")

if __name__ == "__main__":
    # Set start method for multiprocessing
    mp.set_start_method('spawn')
    main()