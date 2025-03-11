#!/usr/bin/env python3
"""
Clustering example for the TwbCompare library.

This script demonstrates how to:
1. Parse a directory of .twb files
2. Cluster them based on structural similarity
3. Analyze commonalities within each cluster
4. Visualize the clusters and their commonalities
"""
import os
import sys
import matplotlib.pyplot as plt
from twbcompare.parser import parse_directory
from twbcompare.clustering import XMLClusterAnalyzer
from twbcompare.analyzer import find_commonalities
from twbcompare.matplotlib_visualizer import visualize_commonalities


def main():
    """Run the clustering example."""
    # Check for input directory argument
    if len(sys.argv) < 2:
        print("Usage: python clustering_example.py /path/to/twb/files")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    print(f"Analyzing and clustering .twb files in {input_dir}")
    
    # Create output directory
    output_dir = "clustering_example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Parse .twb files
    structures = parse_directory(input_dir)
    if not structures:
        print("No valid .twb files found.")
        sys.exit(1)
    
    print(f"Parsed {len(structures)} .twb files successfully")
    
    # 2. Initialize the cluster analyzer
    analyzer = XMLClusterAnalyzer(structures)
    
    # 3. Extract features
    analyzer.extract_features()
    print("Extracted features for clustering")
    
    # 4. Perform clustering (both kmeans and hierarchical)
    methods = ['kmeans', 'hierarchical']
    n_clusters = 3  # You can adjust this or use a different method to determine optimal number
    
    for method in methods:
        print(f"\nClustering with {method} method into {n_clusters} clusters")
        clusters = analyzer.cluster(n_clusters=n_clusters, method=method)
        
        # Create method-specific output directory
        method_dir = os.path.join(output_dir, method)
        os.makedirs(method_dir, exist_ok=True)
        
        # 5. Visualize clusters
        vis_file = os.path.join(method_dir, "clusters")
        vis_path = analyzer.visualize_clusters(vis_file, "png")
        print(f"Cluster visualization saved to {vis_path}")
        
        # 6. For hierarchical clustering, also generate dendrogram
        if method == 'hierarchical':
            dend_file = os.path.join(method_dir, "dendrogram")
            dend_path = analyzer.visualize_dendrogram(dend_file, "png")
            print(f"Dendrogram visualization saved to {dend_path}")
        
        # 7. Find and visualize commonalities within each cluster
        commonalities = analyzer.find_cluster_commonalities()
        
        # 8. Generate cluster comparisons
        comparison_dir = os.path.join(method_dir, "comparisons")
        os.makedirs(comparison_dir, exist_ok=True)
        comparison_vis = analyzer.visualize_cluster_comparisons(commonalities, comparison_dir, "png")
        
        for key, path in comparison_vis.items():
            print(f"Comparison visualization ({key}) saved to {path}")
        
        # 9. Generate individual cluster visualizations
        for cluster_id, cluster_files in clusters.items():
            cluster_dir = os.path.join(method_dir, f"cluster_{cluster_id}")
            os.makedirs(cluster_dir, exist_ok=True)
            
            # Find commonalities in this cluster
            common = commonalities[cluster_id]
            
            # Visualize common structure
            viz_file = os.path.join(cluster_dir, "common_structure")
            viz_path = visualize_commonalities(common, viz_file, "png")
            print(f"Cluster {cluster_id} common structure visualization saved to {viz_path}")
            
            # Save cluster files list
            files_list = os.path.join(cluster_dir, "files.txt")
            with open(files_list, "w") as f:
                for structure in cluster_files:
                    f.write(f"{structure.filename}\n")
    
    print("\nClustering example completed. Check the 'clustering_example_output' directory for results.")


if __name__ == "__main__":
    main() 