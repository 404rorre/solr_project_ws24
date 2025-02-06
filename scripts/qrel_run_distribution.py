import pandas as pd
import plotly.express as px

def load_qrel_file(qrel_path):
    """Load and process QREL file."""
    # Read QREL file without headers
    qrel_df = pd.read_csv(qrel_path, sep=' ', header=None,
                         names=['topic', 'q0', 'docid', 'relevance'])
    
    # Create translation dictionary for relevance scores
    # Only include documents with relevance > 0
    relevance_map = {}
    for _, row in qrel_df.iterrows():
        if row['relevance'] > 0:
            # Map relevance scores: 1 -> 0.5, 2 -> 1.0
            relevance_map[(row['topic'], row['docid'])] = 1.0 if row['relevance'] == 2 else 0.5
    
    return relevance_map

def load_run_file(run_path):
    """Load and process run file."""
    # Read run file without headers
    run_df = pd.read_csv(run_path, sep='\t', header=None,
                        names=['topic', 'Q0', 'docid', 'rank', 'score', 'run_tag'])
    return run_df

def process_results(run_df, relevance_map):
    """Process results and calculate rank-wise relevance scores."""
    # Initialize list to store rank-wise scores
    max_rank = run_df['rank'].max()
    rank_scores = [0] * max_rank
    
    # Process each result
    for _, row in run_df.iterrows():
        topic_doc_key = (row['topic'], row['docid'])
        if topic_doc_key in relevance_map:
            # Add relevance score to the corresponding rank position (0-based indexing)
            rank_scores[row['rank'] - 1] += relevance_map[topic_doc_key]
    
    return rank_scores

def create_visualization(rank_scores):
    """Create visualization of rank-wise relevance scores."""
    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'Rank': range(1, len(rank_scores) + 1),
        'Summed Relevance Score': rank_scores
    })
    
    # Create histogram using plotly express
    fig = px.histogram(
                plot_df, 
                x='Rank', 
                y='Summed Relevance Score',
                title='Distribution of Relevance Scores Across Ranks',
                labels={'Rank': 'Rank Position',
                    'Summed Relevance Score': 'Sum of Relevance Scores'},
                nbins=100
                )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Rank Position",
        yaxis_title="Summed Relevance Score",
        bargap=0.1
    )
    
    return fig

def main():
    # File paths
    qrel_path = 'data/qrel/qrels-covid_d5_j0.5-5.txt'
    run_path = 'runs/processed/base_bm25_90001.run'
    
    # Load and process files
    relevance_map = load_qrel_file(qrel_path)
    run_df = load_run_file(run_path)
    
    # Process results
    rank_scores = process_results(run_df, relevance_map)
    
    # Create visualization
    fig = create_visualization(rank_scores)
    
    # Save visualization
    fig.write_html("relevance_distribution.html")
    fig.show()
    
    # Create and save summary table
    summary_df = pd.DataFrame({
        'Rank': range(1, len(rank_scores) + 1),
        'Summed_Relevance_Score': rank_scores
    })
    summary_df.to_csv('rank_wise_scores.csv', index=False)
    
    print("Analysis complete. Check 'relevance_distribution.html' for visualization")
    print("and 'rank_wise_scores.csv' for detailed scores.")

if __name__ == "__main__":
    main()