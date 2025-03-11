"""
Clustering module for grouping similar .twb files.

This module provides functionality to cluster .twb files based on their
hierarchical structure similarity and depth.
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Set, Tuple
from collections import Counter
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from twbcompare.models import FileStructure, CommonStructure
from twbcompare.analyzer import find_commonalities

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class XMLClusterAnalyzer:
    """
    Class for clustering and analyzing XML files based on their structure.
    """
    
    def __init__(self, structures: List[FileStructure]):
        """
        Initialize a new XMLClusterAnalyzer.
        
        Args:
            structures: List of FileStructure objects to analyze
        """
        self.structures = structures
        self.feature_matrix = None
        self.feature_names = None
        self.model = None
        self.clusters = {}
        self.n_clusters = 0
        self.cluster_labels = []
    
    def extract_features(self, max_depth: int = 5) -> np.ndarray:
        """
        Extract features from the file structures for clustering.
        
        This method generates a feature vector for each file based on:
        - Path presence at each depth level
        - Tag frequencies
        - Path depth distribution
        
        Args:
            max_depth: Maximum path depth to consider
            
        Returns:
            Feature matrix with shape (n_files, n_features)
        """
        logger.info("Extracting features from file structures")
        
        # Collect all unique paths up to max_depth
        all_paths = set()
        for structure in self.structures:
            for path in structure.all_paths:
                # Split path and truncate to max_depth
                parts = path.strip('/').split('/')
                for d in range(1, min(len(parts) + 1, max_depth + 1)):
                    depth_path = '/' + '/'.join(parts[:d])
                    all_paths.add(depth_path)
        
        # Sort paths for consistent feature ordering
        sorted_paths = sorted(all_paths)
        
        # Create feature matrix
        n_files = len(self.structures)
        n_features = len(sorted_paths)
        X = np.zeros((n_files, n_features))
        
        # Populate feature matrix
        for i, structure in enumerate(self.structures):
            for j, path in enumerate(sorted_paths):
                if path in structure.all_paths:
                    # Feature value is 1 if path exists
                    X[i, j] = 1
        
        # Store feature names for interpretation
        self.feature_names = sorted_paths
        self.feature_matrix = X
        
        logger.info(f"Extracted {n_features} features for {n_files} files")
        return X
    
    def compute_depth_features(self) -> np.ndarray:
        """
        Compute depth-based features for clustering.
        
        Returns:
            Depth feature matrix
        """
        logger.info("Computing depth-based features")
        
        # For each file, compute histogram of path depths
        max_depth = 0
        for structure in self.structures:
            for path in structure.all_paths:
                depth = len(path.strip('/').split('/'))
                max_depth = max(max_depth, depth)
        
        # Create depth feature matrix
        n_files = len(self.structures)
        X_depth = np.zeros((n_files, max_depth))
        
        for i, structure in enumerate(self.structures):
            depth_counts = Counter()
            for path in structure.all_paths:
                depth = len(path.strip('/').split('/'))
                depth_counts[depth] += 1
            
            # Normalize by total count
            total = sum(depth_counts.values())
            for depth, count in depth_counts.items():
                X_depth[i, depth-1] = count / total
        
        logger.info(f"Computed depth features with {max_depth} depth levels")
        return X_depth
    
    def cluster(self, n_clusters: int = 3, method: str = 'kmeans', use_depth_features: bool = True) -> Dict[int, List[FileStructure]]:
        """
        Cluster the files based on their features.
        
        Args:
            n_clusters: Number of clusters to create
            method: Clustering method ('kmeans' or 'hierarchical')
            use_depth_features: Whether to include depth distribution features
            
        Returns:
            Dictionary mapping cluster IDs to lists of FileStructure objects
        """
        logger.info(f"Clustering {len(self.structures)} files into {n_clusters} clusters using {method}")
        
        # Extract features if not already done
        if self.feature_matrix is None:
            self.extract_features()
        
        # Combine with depth features if requested
        if use_depth_features:
            depth_features = self.compute_depth_features()
            X = np.hstack((self.feature_matrix, depth_features))
        else:
            X = self.feature_matrix
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply clustering
        if method == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42)
            labels = model.fit_predict(X_scaled)
            self.model = model
        elif method == 'hierarchical':
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X_scaled)
            self.model = model
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        # Group files by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(self.structures[i])
        
        self.clusters = clusters
        self.n_clusters = n_clusters
        self.cluster_labels = labels
        
        # Log cluster sizes
        for cluster_id, cluster_files in clusters.items():
            logger.info(f"Cluster {cluster_id}: {len(cluster_files)} files")
        
        return clusters
    
    def find_cluster_commonalities(self) -> Dict[int, CommonStructure]:
        """
        Find commonalities within each cluster.
        
        Returns:
            Dictionary mapping cluster IDs to CommonStructure objects
        """
        if self.clusters is None:
            raise ValueError("Must run cluster() before finding commonalities")
        
        logger.info("Finding commonalities within each cluster")
        
        commonalities = {}
        for cluster_id, cluster_files in self.clusters.items():
            logger.info(f"Analyzing commonalities in cluster {cluster_id} ({len(cluster_files)} files)")
            common = find_commonalities(cluster_files)
            commonalities[cluster_id] = common
        
        return commonalities
    
    def visualize_clusters(self, output_file: str, output_format: str = "png") -> str:
        """
        Visualize clusters using dimensionality reduction techniques.
        
        Args:
            output_file: Base name for the output file (without extension)
            output_format: Output format (png, svg, or html)
            
        Returns:
            Path to the generated visualization file
        """
        logger.info("Visualizing clusters")
        
        # Extract features for visualization
        X = self.compute_depth_features()
        file_names = [structure.filename for structure in self.structures]
        
        if len(X) <= 1:
            logger.warning("Cannot visualize clusters with only one file")
            return output_file
        
        # For small datasets, adjust perplexity parameter
        # Perplexity must be less than the number of samples
        perplexity = min(2, len(X) - 1)  # Ensure perplexity is at least 2 but less than n_samples
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Use t-SNE for dimensionality reduction if we have enough samples
        if len(X) > 2:
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
            X_2d = tsne.fit_transform(X_scaled)
        else:
            # For very small datasets, use PCA instead
            pca = PCA(n_components=2)
            X_2d = pca.fit_transform(X_scaled)
        
        # If HTML format is requested, create an interactive visualization
        if output_format.lower() == 'html':
            return self._create_interactive_visualization(X_2d, file_names, output_file)
            
        # Otherwise create a static matplotlib visualization
        # Create a larger figure
        plt.figure(figsize=(12, 10))
        
        # Scatter plot with different colors for each cluster
        colors = plt.cm.rainbow(np.linspace(0, 1, len(set(self.cluster_labels))))
        
        for i, (x, y, label, file) in enumerate(zip(X_2d[:, 0], X_2d[:, 1], 
                                                  self.cluster_labels, file_names)):
            plt.scatter(x, y, color=colors[label], s=100, alpha=0.8)
            plt.annotate(os.path.basename(file), (x, y), fontsize=9,
                       xytext=(5, 5), textcoords='offset points')
        
        # Add titles and labels
        plt.title('XML File Clusters by Hierarchy Structure', fontsize=14)
        plt.xlabel('Dimension 1', fontsize=12)
        plt.ylabel('Dimension 2', fontsize=12)
        
        # Add a legend for clusters
        for i in range(len(set(self.cluster_labels))):
            plt.scatter([], [], color=colors[i], label=f'Cluster {i}')
        plt.legend(loc='best')
        
        # Save figure
        full_path = f"{output_file}.{output_format}"
        plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return full_path
        
    def _create_interactive_visualization(self, X_2d, file_names, output_file):
        """
        Create an interactive HTML visualization of clusters using Plotly.
        
        Args:
            X_2d: 2D coordinates for each file
            file_names: List of file names
            output_file: Base output file name
            
        Returns:
            Path to the generated HTML file
        """
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.subplots import make_subplots
        except ImportError:
            logger.warning("Plotly is not installed. Installing it now...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'plotly'])
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.subplots import make_subplots
        
        # Create a DataFrame with the data
        import pandas as pd
        
        # Make sure we have cluster labels
        if not hasattr(self, 'cluster_labels') or len(self.cluster_labels) == 0:
            logger.warning("No cluster labels found. Using default labels.")
            cluster_labels = [0] * len(file_names)
        else:
            cluster_labels = self.cluster_labels
            
        df = pd.DataFrame({
            'x': X_2d[:, 0],
            'y': X_2d[:, 1],
            'cluster': [f'Cluster {label}' for label in cluster_labels],
            'filename': [os.path.basename(f) for f in file_names],
            'full_path': file_names
        })
        
        # Create the figure
        fig = px.scatter(
            df, x='x', y='y', color='cluster',
            hover_data=['filename', 'full_path'],
            title='Interactive XML File Clusters',
            labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
            height=800, width=1000
        )
        
        # Improve the hover template
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>Cluster: %{marker.color}<br>Path: %{customdata[1]}<extra></extra>'
        )
        
        # Improve the layout
        fig.update_layout(
            title_font_size=18,
            legend_title_font_size=14,
            legend_font_size=12,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )
        
        # Save to HTML file
        full_path = f"{output_file}.html"
        fig.write_html(
            full_path,
            include_plotlyjs='cdn',
            full_html=True,
            include_mathjax='cdn'
        )
        
        logger.info(f"Interactive visualization saved to {full_path}")
        return full_path
    
    def visualize_dendrogram(self, output_file: str, output_format: str = "png") -> str:
        """
        Generate a dendrogram visualization for hierarchical clustering.
        
        Args:
            output_file: Base name for the output file (without extension)
            output_format: Output format (png or svg)
            
        Returns:
            Path to the generated visualization file
        """
        if not hasattr(self, 'model') or self.model is None:
            raise ValueError("Must run cluster() before visualization")
        
        # Use PNG format for matplotlib visualizations if HTML was specified
        actual_format = "png" if output_format.lower() == "html" else output_format
        
        # Extract features for hierarchical clustering
        X = self.compute_depth_features()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Compute linkage matrix
        Z = linkage(X_scaled, method='ward')
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create dendrogram
        dendrogram(
            Z,
            labels=[os.path.basename(s.filename) for s in self.structures],
            leaf_rotation=90.0,
            leaf_font_size=8.0,
            show_contracted=True,
        )
        
        plt.title("Hierarchical Clustering Dendrogram", fontsize=14)
        plt.xlabel("File", fontsize=12)
        plt.ylabel("Distance", fontsize=12)
        plt.tight_layout()
        
        # Save the figure
        output_path = f"{output_file}.{actual_format}"
        plt.savefig(output_path, format=actual_format, dpi=300)
        plt.close()
        
        logger.info(f"Dendrogram visualization saved to {output_path}")
        return output_path
    
    def visualize_cluster_comparisons(self, commonalities: Dict[int, CommonStructure], 
                                      output_dir: str, output_format: str = "png") -> Dict[int, str]:
        """
        Generate visualizations comparing the common elements across clusters.
        
        Args:
            commonalities: Dictionary mapping cluster IDs to CommonStructure objects
            output_dir: Directory for output files
            output_format: Output format (png or svg)
            
        Returns:
            Dictionary mapping cluster IDs to paths of generated visualization files
        """
        if self.clusters is None:
            raise ValueError("Must run cluster() before visualization")
        
        logger.info("Generating cluster comparison visualizations")
        
        os.makedirs(output_dir, exist_ok=True)
        output_paths = {}
        
        # Use PNG format for matplotlib visualizations if HTML was specified
        actual_format = "png" if output_format.lower() == "html" else output_format
        
        # Create a heatmap showing path presence across clusters
        plt.figure(figsize=(14, 10))
        
        # Collect all paths from all clusters
        all_paths = set()
        for common in commonalities.values():
            all_paths.update(common.common_paths)
        
        # Sort paths for consistent ordering
        sorted_paths = sorted(all_paths)
        
        # Create a matrix of path presence
        cluster_ids = sorted(commonalities.keys())
        presence_matrix = np.zeros((len(sorted_paths), len(cluster_ids)))
        
        for i, path in enumerate(sorted_paths):
            for j, cluster_id in enumerate(cluster_ids):
                if path in commonalities[cluster_id].common_paths:
                    # Use frequency as value
                    presence_matrix[i, j] = commonalities[cluster_id].path_frequency.get(path, 0)
        
        # Create a heatmap
        plt.imshow(presence_matrix, cmap='viridis', aspect='auto')
        plt.colorbar(label='Frequency')
        
        # Add labels
        plt.yticks(range(len(sorted_paths)), [p.split('/')[-1] if p else '/' for p in sorted_paths], fontsize=8)
        plt.xticks(range(len(cluster_ids)), [f'Cluster {i}' for i in cluster_ids])
        
        plt.title("Common Paths Across Clusters")
        plt.tight_layout()
        
        # Save the figure
        output_path = os.path.join(output_dir, f"cluster_comparison.{actual_format}")
        plt.savefig(output_path, format=actual_format, dpi=300)
        plt.close()
        
        logger.info(f"Cluster comparison visualization saved to {output_path}")
        output_paths['comparison'] = output_path
        
        # Create depth distribution plots for each cluster
        plt.figure(figsize=(12, 8))
        
        for cluster_id, files in self.clusters.items():
            depths = []
            for structure in files:
                for path in structure.all_paths:
                    depth = len(path.strip('/').split('/'))
                    depths.append(depth)
            
            plt.hist(depths, alpha=0.5, bins=range(1, max(depths) + 2), label=f'Cluster {cluster_id}')
        
        plt.title("Path Depth Distribution by Cluster")
        plt.xlabel("Path Depth")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        # Save the figure
        output_path = os.path.join(output_dir, f"depth_distribution.{actual_format}")
        plt.savefig(output_path, format=actual_format, dpi=300)
        plt.close()
        
        logger.info(f"Depth distribution visualization saved to {output_path}")
        output_paths['depth'] = output_path
        
        return output_paths


def cluster_xml_files(structures: List[FileStructure], n_clusters: int = 3,
                     method: str = 'kmeans', output_dir: str = None,
                     output_format: str = "png") -> Tuple[Dict[int, List[FileStructure]], Dict[str, str]]:
    """
    Cluster XML files and generate visualizations.
    
    Args:
        structures: List of FileStructure objects to cluster
        n_clusters: Number of clusters to create
        method: Clustering method ('kmeans' or 'hierarchical')
        output_dir: Directory for output files
        output_format: Output format (png, svg, or html - html creates an interactive visualization for clusters)
        
    Returns:
        Tuple containing:
        - Dictionary mapping cluster IDs to lists of FileStructure objects
        - Dictionary mapping visualization names to file paths
    """
    logger.info(f"Clustering {len(structures)} XML files into {n_clusters} clusters")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "cluster_output"
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize cluster analyzer
    analyzer = XMLClusterAnalyzer(structures)
    
    # Extract features and cluster
    analyzer.extract_features()
    clusters = analyzer.cluster(n_clusters=n_clusters, method=method)
    
    # Find commonalities within each cluster
    commonalities = analyzer.find_cluster_commonalities()
    
    # Generate visualizations
    visualizations = {}
    
    # Cluster scatter plot
    vis_file = os.path.join(output_dir, "clusters")
    visualizations['clusters'] = analyzer.visualize_clusters(vis_file, output_format)
    
    # Dendrogram (for hierarchical clustering)
    if method == 'hierarchical':
        vis_file = os.path.join(output_dir, "dendrogram")
        visualizations['dendrogram'] = analyzer.visualize_dendrogram(vis_file, output_format)
    
    # Cluster comparisons
    comparison_dir = os.path.join(output_dir, "comparisons")
    os.makedirs(comparison_dir, exist_ok=True)
    comparison_vis = analyzer.visualize_cluster_comparisons(commonalities, comparison_dir, output_format)
    for key, path in comparison_vis.items():
        visualizations[f'comparison_{key}'] = path
    
    return clusters, visualizations 