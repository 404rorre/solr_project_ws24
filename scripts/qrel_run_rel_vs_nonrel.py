import pandas as pd
import plotly.express as px
import numpy as np

def load_qrel_file(qrel_path):
    """Load and process QREL file."""
    qrel_df = pd.read_csv(qrel_path, sep=' ', header=None,
                         names=['topic', 'q0', 'docid', 'relevance'])
    
    # Create dictionary mapping (topic, docid) to relevance
    relevance_map = {}
    for _, row in qrel_df.iterrows():
        relevance_map[(row['topic'], row['docid'])] = row['relevance']
    
    return relevance_map

def load_run_file(run_path):
    """Load and process run file."""
    run_df = pd.read_csv(run_path, sep='\t', header=None,
                        names=['topic', 'Q0', 'docid', 'rank', 'score', 'run_tag'])
    return run_df

def process_results_by_bins(run_df, relevance_map, bin_size=10):
    """Process results and calculate relevance distribution in bins."""
    max_rank = run_df['rank'].max()
    num_bins = (max_rank + bin_size - 1) // bin_size  # Round up to nearest bin
    
    # Initialize counters for each bin
    non_relevant = [0] * num_bins
    relevant = [0] * num_bins
    highly_relevant = [0] * num_bins
    not_in_qrel = [0] * num_bins
    
    # Process each result
    for _, row in run_df.iterrows():
        topic_doc_key = (row['topic'], row['docid'])
        bin_index = (row['rank'] - 1) // bin_size
        
        if topic_doc_key in relevance_map:
            rel_score = relevance_map[topic_doc_key]
            if rel_score == 0:
                non_relevant[bin_index] += 1
            elif rel_score == 1:
                relevant[bin_index] += 1
            elif rel_score == 2:
                highly_relevant[bin_index] += 1
        else:
            not_in_qrel[bin_index] += 1
    
    # Create bin labels
    bin_labels = [f"{i*bin_size + 1}-{min((i+1)*bin_size, max_rank)}" 
                 for i in range(num_bins)]
    
    return {
        'bin_labels': bin_labels,
        'non_relevant': non_relevant,
        'relevant': relevant,
        'highly_relevant': highly_relevant,
        'not_in_qrel': not_in_qrel
    }

def create_stacked_visualization(binned_results, title="Distribution of Document Relevance by Rank"):
    """Create stacked bar visualization of relevance distribution."""
    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'Rank_Bins': binned_results['bin_labels'],
        'Non-Relevant': binned_results['non_relevant'],
        'Relevant': binned_results['relevant'],
        'Highly Relevant': binned_results['highly_relevant'],
        'Not in QREL': binned_results['not_in_qrel']
    })
    
    # Melt the DataFrame for plotting
    plot_df_melted = pd.melt(
        plot_df, 
        id_vars=['Rank_Bins'], 
        value_vars=['Non-Relevant', 'Relevant', 'Highly Relevant', 'Not in QREL'],
        var_name='Relevance_Category',
        value_name='Count'
    )
    
    # Create stacked bar chart
    fig = px.bar(plot_df_melted,
                 x='Rank_Bins',
                 y='Count',
                 color='Relevance_Category',
                 title=title,
                 labels={'Rank_Bins': 'Rank Ranges',
                        'Count': 'Number of Documents',
                        'Relevance_Category': 'Relevance Category'},
                 color_discrete_map={
                     'Non-Relevant': 'red',
                     'Relevant': 'yellow',
                     'Highly Relevant': 'green',
                     'Not in QREL': 'gray'
                 })
    
    # Update layout
    fig.update_layout(
        xaxis_title="Rank Ranges",
        yaxis_title="Number of Documents",
        bargap=0.1,
        legend_title="Relevance Category"
    )
    
    return fig

def save_summary_table(binned_results, output_path):
    """Save summary table of binned results."""
    summary_df = pd.DataFrame({
        'Rank_Bins': binned_results['bin_labels'],
        'Non_Relevant': binned_results['non_relevant'],
        'Relevant': binned_results['relevant'],
        'Highly_Relevant': binned_results['highly_relevant'],
        'Not_in_QREL': binned_results['not_in_qrel']
    })
    summary_df.to_csv(output_path, index=False)

def main():
    # Configuration
    bin_size = 10  # You can change this value to adjust bin size
    
    # File paths
    qrel_path = 'data/qrel/qrels-covid_d5_j0.5-5.txt'
    run_path = 'runs/processed/DIS17-2024-assignment3-BLACKBOX-textEN_bm25_nltk_cit_1.run'
    
    # Load and process files
    relevance_map = load_qrel_file(qrel_path)
    run_df = load_run_file(run_path)
    
    # Process results with binning
    binned_results = process_results_by_bins(run_df, relevance_map, bin_size)
    
    # Create visualization
    fig = create_stacked_visualization(binned_results)
    
    # Save outputs
    fig.write_html(f"relevance_distribution_bins_{bin_size}.html")
    fig.show()
    save_summary_table(binned_results, f"rank_wise_scores_bins_{bin_size}.csv")
    
    print(f"Analysis complete. Check 'relevance_distribution_bins_{bin_size}.html' for visualization")
    print(f"and 'rank_wise_scores_bins_{bin_size}.csv' for detailed scores.")

if __name__ == "__main__":
    main()