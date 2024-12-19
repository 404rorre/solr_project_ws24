import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from tqdm import tqdm
import networkx as nx
import community.community_louvain as community_louvain
import multiprocessing as mp
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

def analyze_document_topic_distribution(df: pd.DataFrame) -> Tuple[Dict, Dict, Dict, Dict]:
    """
    Analyze distribution of documents across topics and find shared documents.
    Now includes count of documents exclusive to each topic.
    """
    # Count topics per document
    doc_topic_counts = df.groupby('cord_uid')['topic'].nunique()
    distribution = Counter(doc_topic_counts)
    
    # Count unique documents per topic
    topic_counts = df.groupby('topic')['cord_uid'].nunique().to_dict()
    
    # Create topic-document mapping
    topic_docs = defaultdict(set)
    doc_topic_dict = defaultdict(set)
    for _, row in df.iterrows():
        topic_docs[row['topic']].add(row['cord_uid'])
        doc_topic_dict[row['cord_uid']].add(row['topic'])
    
    # Count exclusive documents (documents that appear in only this topic)
    exclusive_counts = {}
    for topic, docs in topic_docs.items():
        exclusive_docs = {doc for doc in docs if len(doc_topic_dict[doc]) == 1}
        exclusive_counts[topic] = len(exclusive_docs)
    
    # Find shared documents between topics
    topics = sorted(topic_docs.keys())
    topic_overlaps = defaultdict(list)
    
    for t1, t2 in combinations(topics, 2):
        shared_docs = topic_docs[t1] & topic_docs[t2]
        if shared_docs:
            topic_overlaps[t1].append((t2, len(shared_docs), shared_docs))
            topic_overlaps[t2].append((t1, len(shared_docs), shared_docs))
    
    return distribution, topic_overlaps, topic_counts, exclusive_counts

def process_cluster_chunk(chunk_data):
    """Process a chunk of document pairs for clustering."""
    doc_topic_dict, doc_pairs = chunk_data
    edges = []
    
    for doc1, doc2 in doc_pairs:
        shared_topics = len(doc_topic_dict[doc1] & doc_topic_dict[doc2])
        if shared_topics > 0:
            edges.append((doc1, doc2, shared_topics))
    
    return edges

def export_analysis_to_markdown(distribution: Dict, 
                              topic_overlaps: Dict,
                              topic_counts: Dict,
                              exclusive_counts: Dict,
                              clusters: Dict,
                              cluster_topics: Dict,
                              output_file: str):
    """Export all analysis results to markdown format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Document-Topic Distribution and Clustering Analysis\n\n")
        
        # Topic Counts with Exclusive Documents
        f.write("## 1. Documents per Topic\n\n")
        f.write("| Topic | Total Documents | Exclusive Documents | % Exclusive |\n")
        f.write("|-------|-----------------|-------------------|-------------|\n")
        for topic in sorted(topic_counts.keys()):
            total = topic_counts[topic]
            exclusive = exclusive_counts[topic]
            exclusive_pct = (exclusive / total) * 100
            f.write(f"| {topic} | {total:,} | {exclusive:,} | {exclusive_pct:.1f}% |\n")
        
        # Part 2: Overall Distribution
        f.write("\n## 2. Document Distribution Across Topics\n\n")
        total_docs = sum(distribution.values())
        cumulative = 0
        
        f.write("| Topics | Documents | Percentage | Cumulative % |\n")
        f.write("|--------|------------|------------|-------------|\n")
        
        for num_topics, num_docs in sorted(distribution.items()):
            cumulative += num_docs
            percentage = (num_docs / total_docs) * 100
            cum_percentage = (cumulative / total_docs) * 100
            f.write(f"| {num_topics} | {num_docs:,} | {percentage:.1f}% | {cum_percentage:.1f}% |\n")
            
        # Part 3: Topic Overlaps
        f.write("\n## 3. Topic Overlap Analysis\n\n")
        
        for topic in sorted(topic_overlaps.keys()):
            f.write(f"\n### Topic {topic}\n\n")
            f.write(f"Total Documents: {topic_counts[topic]:,}\n")
            f.write(f"Exclusive Documents: {exclusive_counts[topic]:,} ({(exclusive_counts[topic]/topic_counts[topic])*100:.1f}%)\n\n")
            
            # Sort overlaps by number of shared documents
            sorted_overlaps = sorted(topic_overlaps[topic], key=lambda x: x[1], reverse=True)
            
            f.write("| Related Topic | Shared Documents | % of Topic Documents | Rank |\n")
            f.write("|---------------|-----------------|-------------------|------|\n")
            
            for rank, (related_topic, shared_count, _) in enumerate(sorted_overlaps, 1):
                percentage = (shared_count / topic_counts[topic]) * 100
                f.write(f"| {related_topic} | {shared_count:,} | {percentage:.1f}% | {rank} |\n")
        
        # Part 4: Document Clusters
        f.write("\n## 4. Document Clusters Analysis\n\n")
        
        for cluster_id in sorted(clusters.keys()):
            f.write(f"\n### Cluster {cluster_id}\n\n")
            docs_in_cluster = len(clusters[cluster_id])
            topics_in_cluster = len(cluster_topics[cluster_id])
            
            f.write(f"**Cluster Statistics:**\n")
            f.write(f"- Documents: {docs_in_cluster:,}\n")
            f.write(f"- Unique topics: {topics_in_cluster}\n\n")
            
            f.write("**Top Topics:**\n\n")
            f.write("| Topic | Total Docs | Docs in Cluster | % of Cluster | % of Topic Total |\n")
            f.write("|-------|------------|-----------------|--------------|------------------|\n")
            
            top_topics = sorted(cluster_topics[cluster_id].items(), key=lambda x: x[1], reverse=True)
            for topic, count in top_topics[:5]:
                cluster_percentage = (count / docs_in_cluster) * 100
                topic_percentage = (count / topic_counts[topic]) * 100
                f.write(f"| {topic} | {topic_counts[topic]:,} | {count:,} | {cluster_percentage:.1f}% | {topic_percentage:.1f}% |\n")

def main():
    print("Loading data...")
    qrels_df = pd.read_csv("data/qrel/qrels-covid_d5_j0.5-5.txt", 
                          sep=' ', 
                          header=None,
                          names=['topic', 'iteration', 'cord_uid', 'relevance'])
    
    # Filter for relevant documents
    relevant_df = qrels_df[qrels_df['relevance'] > 0]
    
    print("Analyzing document-topic distribution...")
    distribution, topic_overlaps, topic_counts, exclusive_counts = analyze_document_topic_distribution(relevant_df)
    
    # Create document-topic dictionary for clustering
    doc_topic_dict = defaultdict(set)
    for _, row in relevant_df.iterrows():
        doc_topic_dict[row['cord_uid']].add(row['topic'])
    
    print("\nClustering documents...")
    # Create document pairs for parallel processing
    docs = list(doc_topic_dict.keys())
    doc_pairs = list(combinations(docs, 2))
    
    # Split pairs into chunks for parallel processing
    n_processes = mp.cpu_count()
    chunk_size = len(doc_pairs) // (n_processes * 4)
    chunks = [doc_pairs[i:i + chunk_size] for i in range(0, len(doc_pairs), chunk_size)]
    chunk_data = [(doc_topic_dict, chunk) for chunk in chunks]
    
    # Process chunks in parallel
    print(f"Processing {len(chunks)} chunks using {n_processes} processes...")
    with mp.Pool(processes=n_processes) as pool:
        results = []
        for chunk_result in tqdm(pool.imap(process_cluster_chunk, chunk_data), 
                               total=len(chunks),
                               desc="Processing document pairs"):
            results.extend(chunk_result)
    
    # Create and analyze graph
    G = nx.Graph()
    G.add_weighted_edges_from(results)
    
    print("Detecting communities...")
    communities = community_louvain.best_partition(G)
    
    # Organize documents by community
    clusters = defaultdict(list)
    for doc, cluster_id in communities.items():
        clusters[cluster_id].append(doc)
    
    # Analyze topics in each cluster
    cluster_topics = {}
    for cluster_id, docs in clusters.items():
        cluster_topics[cluster_id] = Counter()
        for doc in docs:
            for topic in doc_topic_dict[doc]:
                cluster_topics[cluster_id][topic] += 1
    
    # Export results
    print("Exporting results to markdown...")
    export_analysis_to_markdown(distribution, topic_overlaps, topic_counts,
                              exclusive_counts, clusters, cluster_topics, 
                              'enhanced_topic_analysis.md')
    print("Analysis complete. Results saved to 'enhanced_topic_analysis.md'")

if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()