import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

class MetadataAnalyzer:
    def __init__(self, base_path: str, columns_to_analyze: List[str]):
        self.base_path = Path(base_path)
        self.columns_to_analyze = columns_to_analyze
        self.metadata_path = self.base_path / "data" / "2020-07-16" / "metadata.csv"
        self.qrels_path = self.base_path / "data" / "qrel" / "qrels-covid_d5_j0.5-5.txt"

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and prepare both datasets"""
        df_meta = pd.read_csv(self.metadata_path)
        qrels_df = pd.read_csv(
            self.qrels_path,
            sep=' ',
            header=None,
            names=['topic', 'iteration', 'cord_uid', 'relevance']
        )
        
        # Group by cord_uid and take the maximum relevance score across topics
        qrels_unique = (qrels_df.groupby('cord_uid')
                       .agg({
                           'relevance': 'max',  # Take highest relevance score
                           'topic': lambda x: list(set(x))  # Keep list of topics
                       })
                       .reset_index())
        
        return df_meta, qrels_unique

    def get_completion_stats(self, df: pd.DataFrame, field: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Calculate completion statistics with consistent dimensions"""
        # Create base crosstab
        cross_tab = pd.crosstab(
            df[field].isnull(),
            df['relevance'],
            margins=False
        )

        # Ensure all relevance levels are present
        for rel in [0, 1, 2]:
            if rel not in cross_tab.columns:
                cross_tab[rel] = 0
        
        # Sort columns and rename
        cross_tab = cross_tab.reindex(columns=[0, 1, 2])
        cross_tab.columns = ['Not Relevant (0)', 'Relevant (1)', 'Highly Relevant (2)']
        cross_tab.index = ['Complete', 'Missing'] if len(cross_tab.index) == 2 else ['Complete']

        # Calculate row totals
        cross_tab['Total'] = cross_tab.sum(axis=1)

        # Calculate percentages based on the total number of documents
        total_docs = cross_tab['Total'].sum()  # Sum of all documents
        percentages = cross_tab.copy()
        for col in percentages.columns:
            percentages[col] = (cross_tab[col] / total_docs * 100)

        return cross_tab, percentages

    def get_topic_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate per-topic statistics"""
        topic_stats = []
        
        # Explode the topics list to create rows for each topic a document belongs to
        exploded_df = df.explode('topic')
        
        for topic in sorted(exploded_df['topic'].unique()):
            topic_docs = exploded_df[exploded_df['topic'] == topic]
            relevant_docs = topic_docs[topic_docs['relevance'] > 0]
            
            stats = {
                'topic': topic,
                'unique_docs': len(topic_docs),
                'relevant_docs': len(relevant_docs),
                'highly_relevant': len(topic_docs[topic_docs['relevance'] == 2])
            }
            
            # Calculate stats for each analyzed column
            for col in self.columns_to_analyze:
                missing = topic_docs[col].isnull().sum()
                rel_missing = len(relevant_docs[relevant_docs[col].isnull()])
                
                stats.update({
                    f'missing_{col}': missing,
                    f'relevant_missing_{col}': rel_missing,
                    f'pct_missing_{col}': (rel_missing / len(relevant_docs) * 100) 
                        if len(relevant_docs) > 0 else 0
                })
            
            topic_stats.append(stats)
        
        return pd.DataFrame(topic_stats)

    def analyze(self) -> Dict[str, Any]:
        """Perform complete analysis"""
        print("Loading data...")
        df_meta, qrels_df = self.load_data()
        
        print("Merging datasets...")
        merged_df = pd.merge(qrels_df, df_meta, on='cord_uid', how='left')
        
        results = {}
        
        # Analyze each column
        for column in self.columns_to_analyze:
            print(f"Analyzing {column}...")
            stats, pct = self.get_completion_stats(merged_df, column)
            results[f'{column}_stats'] = stats
            results[f'{column}_percentages'] = pct
        
        # Get topic statistics
        print("Analyzing topics...")
        results['topic_stats'] = self.get_topic_stats(merged_df)
        
        return results

def print_analysis(results: Dict[str, Any], columns_analyzed: List[str]):
    """Print formatted analysis results"""
    for column in columns_analyzed:
        print(f"\n=== {column.capitalize()} Completion Analysis ===")
        print("\nRaw counts:")
        print(results[f'{column}_stats'])
        print("\nPercentages (%):")
        print(results[f'{column}_percentages'].round(2))

    print("\n=== Missing Metadata Analysis by Topic ===")
    topic_stats = results['topic_stats']
    
    for column in columns_analyzed:
        print(f"\nTop 10 topics with missing {column}:")
        cols_to_show = ['topic', 'relevant_docs',
                       f'relevant_missing_{column}',
                       f'pct_missing_{column}']
        print(topic_stats.sort_values(f'pct_missing_{column}', ascending=False)[
            cols_to_show
        ].head(10).round(2))

def main():
    # Configure analysis
    columns_to_check = ['title', 'abstract']
    
    # Run analysis
    analyzer = MetadataAnalyzer(".", columns_to_check)
    results = analyzer.analyze()
    
    # Print results
    print_analysis(results, columns_to_check)
    
    # Save detailed results
    results['topic_stats'].to_csv("data_manipulation/missing_metadata_analysis.csv", index=False)
    print("\nDetailed results saved to 'missing_metadata_analysis.csv'")

if __name__ == "__main__":
    main()