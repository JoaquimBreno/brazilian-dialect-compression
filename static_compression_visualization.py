import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
import os

def ensure_dir(directory):
    """Make sure a directory exists, creating it if necessary"""
    os.makedirs(directory, exist_ok=True)

def plot_heatmap(matrix, title, filename, cmap='viridis_r', annot=True):
    """Create a heatmap visualization from a matrix."""
    plt.figure(figsize=(10, 8))
    
    # Plot the heatmap
    sns.heatmap(
        matrix, 
        annot=annot, 
        fmt=".4f",
        cmap=cmap,
        linewidths=.5,
        square=True,
        cbar_kws={"shrink": .8}
    )
    
    plt.title(title, fontsize=16)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Saved heatmap to {filename}")
    plt.close()

def plot_dendrogram(matrix, title, filename):
    """Create a dendrogram from a distance matrix."""
    plt.figure(figsize=(12, 8))
    
    # Create a distance matrix
    # In the context of compression distances, smaller is more similar
    # Ensure the matrix is symmetric
    matrix_array = matrix.values
    
    # Convert to a condensed distance matrix
    condensed_dist = squareform(matrix_array)
    
    # Compute hierarchical clustering
    Z = hierarchy.linkage(condensed_dist, method='average')
    
    # Plot the dendrogram
    hierarchy.dendrogram(
        Z,
        labels=matrix.index,
        orientation='right',
        leaf_font_size=12,
        color_threshold=0.7 * max(Z[:,2])
    )
    
    plt.title(title, fontsize=16)
    plt.xlabel('Distance', fontsize=12)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Saved dendrogram to {filename}")
    plt.close()

def normalize_matrix(matrix):
    """
    Normalize the matrix values to a 0-1 scale.
    This makes it easier to compare different metrics.
    """
    min_val = matrix.values.min()
    max_val = matrix.values.max()
    
    if max_val == min_val:
        return matrix
        
    normalized = (matrix - min_val) / (max_val - min_val)
    return normalized

def visualize_static_compression_results():
    """Create visualizations for static compression results."""
    # Ensure output directory exists
    ensure_dir("results/static_compression/visualizations")
    
    # Load the matrices
    try:
        cross_entropy = pd.read_csv("results/static_compression/cross_entropy_matrix.csv", index_col=0)
        kl_divergence = pd.read_csv("results/static_compression/kl_divergence_matrix.csv", index_col=0)
    except FileNotFoundError:
        print("Error: Matrix files not found. Run the static_compression.py script first.")
        return
    
    # Create heatmaps for the raw matrices
    plot_heatmap(
        cross_entropy, 
        "Cross-Entropy Between Regions (Static Model)",
        "results/static_compression/visualizations/cross_entropy_heatmap.png",
        cmap="YlOrRd"
    )
    
    plot_heatmap(
        kl_divergence, 
        "KL Divergence Between Regions (Static Model)",
        "results/static_compression/visualizations/kl_divergence_heatmap.png",
        cmap="YlOrRd"
    )
    
    # Create normalized versions of the matrices
    cross_entropy_norm = normalize_matrix(cross_entropy)
    kl_divergence_norm = normalize_matrix(kl_divergence)
    
    # Save the normalized matrices
    cross_entropy_norm.to_csv("results/static_compression/cross_entropy_normalized.csv")
    kl_divergence_norm.to_csv("results/static_compression/kl_divergence_normalized.csv")
    
    # Create heatmaps for the normalized matrices
    plot_heatmap(
        cross_entropy_norm, 
        "Normalized Cross-Entropy Between Regions (Static Model)",
        "results/static_compression/visualizations/cross_entropy_normalized_heatmap.png",
        cmap="YlOrRd"
    )
    
    plot_heatmap(
        kl_divergence_norm, 
        "Normalized KL Divergence Between Regions (Static Model)",
        "results/static_compression/visualizations/kl_divergence_normalized_heatmap.png",
        cmap="YlOrRd"
    )
    
    # Create dendrograms
    plot_dendrogram(
        cross_entropy, 
        "Hierarchical Clustering Based on Cross-Entropy (Static Model)",
        "results/static_compression/visualizations/cross_entropy_dendrogram.png"
    )
    
    plot_dendrogram(
        kl_divergence, 
        "Hierarchical Clustering Based on KL Divergence (Static Model)",
        "results/static_compression/visualizations/kl_divergence_dendrogram.png"
    )
    
    print("All visualizations completed and saved to results/static_compression/visualizations/")

if __name__ == "__main__":
    visualize_static_compression_results() 