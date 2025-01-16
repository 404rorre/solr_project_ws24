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
    """Process results and calculate relevance distribution in bins as percentages."""
    max_rank = run_df['rank'].max()
    num_bins = (max_rank + bin_size - 1) // bin_size  # Round up to nearest bin
    
    # Initialize counters for each bin
    non_relevant = [0] * num_bins
    relevant = [0] * num_bins
    highly_relevant = [0] * num_bins
    
    # Process each result
    for _, row in run_df.iterrows():
        topic_doc_key = (row['topic'], row['docid'])
        bin_index = (row['rank'] - 1) // bin_size
        
        if topic_doc_key in relevance_map:  # Only process documents that are in QREL
            rel_score = relevance_map[topic_doc_key]
            if rel_score == 0:
                non_relevant[bin_index] += 1
            elif rel_score == 1:
                relevant[bin_index] += 1
            elif rel_score == 2:
                highly_relevant[bin_index] += 1
    
    # Convert to percentages
    percentages = []
    for i in range(num_bins):
        total = non_relevant[i] + relevant[i] + highly_relevant[i]
        if total > 0:
            percentages.append({
                'non_relevant': (non_relevant[i] / total) * 100,
                'relevant': (relevant[i] / total) * 100,
                'highly_relevant': (highly_relevant[i] / total) * 100
            })
        else:
            percentages.append({
                'non_relevant': 0,
                'relevant': 0,
                'highly_relevant': 0
            })
    
    # Create bin labels
    bin_labels = [f"{i*bin_size + 1}-{min((i+1)*bin_size, max_rank)}" 
                 for i in range(num_bins)]
    
    return {
        'bin_labels': bin_labels,
        'percentages': percentages,
        'raw_counts': {
            'non_relevant': non_relevant,
            'relevant': relevant,
            'highly_relevant': highly_relevant
        }
    }

def create_percentage_visualization(binned_results, title="Percentage Distribution of Document Relevance by Rank"):
    """Create 100% stacked bar visualization of relevance distribution."""
    # Create DataFrame for plotting
    data = []
    for i, bin_label in enumerate(binned_results['bin_labels']):
        for category in ['non_relevant', 'relevant', 'highly_relevant']:
            data.append({
                'Rank_Bins': bin_label,
                'Relevance_Category': category.replace('_', ' ').title(),
                'Percentage': binned_results['percentages'][i][category],
                'Raw_Count': binned_results['raw_counts'][category][i]
            })
    
    plot_df = pd.DataFrame(data)
    
    # Create 100% stacked bar chart
    fig = px.bar(plot_df,
                 x='Rank_Bins',
                 y='Percentage',
                 color='Relevance_Category',
                 title=title,
                 labels={'Rank_Bins': 'Rank Ranges',
                        'Percentage': 'Percentage of Documents',
                        'Relevance_Category': 'Relevance Category'},
                 color_discrete_map={
                     'Non Relevant': 'red',
                     'Relevant': 'yellow',
                     'Highly Relevant': 'green'
                 })
    
    # Update layout
    fig.update_layout(
        xaxis_title="Rank Ranges",
        yaxis_title="Percentage of Documents",
        yaxis=dict(tickformat=".1f"),
        bargap=0.1,
        legend_title="Relevance Category"
    )
    
    # Add hover template to show both percentage and raw count
    fig.update_traces(
        hovertemplate="Rank Range: %{x}<br>" +
                     "Category: %{customdata}<br>" +
                     "Percentage: %{y:.1f}%<br>" +
                     "Count: %{text}<br>" +
                     "<extra></extra>",
        customdata=plot_df['Relevance_Category'],
        text=plot_df['Raw_Count']
    )
    
    return fig

def save_summary_table(binned_results, output_path):
    """Save summary table of binned results with both percentages and raw counts."""
    summary_data = []
    for i, bin_label in enumerate(binned_results['bin_labels']):
        summary_data.append({
            'Rank_Bins': bin_label,
            'Non_Relevant_Percent': binned_results['percentages'][i]['non_relevant'],
            'Relevant_Percent': binned_results['percentages'][i]['relevant'],
            'Highly_Relevant_Percent': binned_results['percentages'][i]['highly_relevant'],
            'Non_Relevant_Count': binned_results['raw_counts']['non_relevant'][i],
            'Relevant_Count': binned_results['raw_counts']['relevant'][i],
            'Highly_Relevant_Count': binned_results['raw_counts']['highly_relevant'][i]
        })
    
    summary_df = pd.DataFrame(summary_data)
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
    fig = create_percentage_visualization(binned_results)
    
    # Save outputs
    fig.write_html(f"relevance_percentage_distribution_bins_{bin_size}.html")
    fig.show()
    save_summary_table(binned_results, f"rank_wise_percentage_scores_bins_{bin_size}.csv")
    
    print(f"Analysis complete. Check 'relevance_percentage_distribution_bins_{bin_size}.html' for visualization")
    print(f"and 'rank_wise_percentage_scores_bins_{bin_size}.csv' for detailed scores.")

if __name__ == "__main__":
    main()