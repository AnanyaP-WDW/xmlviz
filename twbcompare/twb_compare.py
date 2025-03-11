#!/usr/bin/env python3
"""
TwbCompare - A tool for analyzing, comparing, and visualizing Tableau .twb files.

This is the main script that provides the command-line interface for the tool.
"""
import os
import sys
import argparse
import logging
import json
from typing import List, Dict, Optional, Tuple

from twbcompare.parser import parse_directory, parse_twb
from twbcompare.analyzer import find_commonalities, get_stats_report
from twbcompare.matplotlib_visualizer import (
    visualize_structure, 
    visualize_commonalities,
    visualize_file_structure
)
from twbcompare.generator import generate_mock_twb, generate_mock_twb_with_placeholders
from twbcompare.models import FileStructure, CommonStructure
from twbcompare.clustering import cluster_xml_files, XMLClusterAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TwbCompare - Analyze and compare Tableau .twb files"
    )
    
    parser.add_argument(
        "input_dir",
        help="Directory containing .twb files to analyze"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory for output files",
        default="twbcompare_output"
    )
    
    parser.add_argument(
        "-t", "--threshold",
        help="Minimum frequency threshold for commonality (0.0-1.0)",
        type=float,
        default=1.0
    )
    
    parser.add_argument(
        "-f", "--format",
        help="Output format for visualizations (html recommended for interactive cluster visualization)",
        choices=["png", "svg", "html"],
        default="html"
    )
    
    parser.add_argument(
        "--no-viz",
        help="Skip visualization generation",
        action="store_true"
    )
    
    parser.add_argument(
        "--no-mock",
        help="Skip mock .twb file generation",
        action="store_true"
    )
    
    parser.add_argument(
        "--placeholders",
        help="Use placeholder values for empty attributes in the mock .twb file",
        action="store_true"
    )
    
    parser.add_argument(
        "--json",
        help="Output report in JSON format",
        action="store_true"
    )
    
    parser.add_argument(
        "--verbose",
        help="Enable verbose logging",
        action="store_true"
    )
    
    # Add clustering arguments
    parser.add_argument(
        "--cluster",
        help="Perform clustering of .twb files",
        action="store_true"
    )
    
    parser.add_argument(
        "--n-clusters",
        help="Number of clusters to create",
        type=int,
        default=3
    )
    
    parser.add_argument(
        "--cluster-method",
        help="Clustering method to use",
        choices=["kmeans", "hierarchical"],
        default="kmeans"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    if args.threshold < 0.0 or args.threshold > 1.0:
        logger.error(f"Threshold must be between 0.0 and 1.0, got {args.threshold}")
        sys.exit(1)
    
    return args


def run_analysis(args: argparse.Namespace) -> Tuple[List[FileStructure], CommonStructure]:
    """
    Run the analysis on .twb files.
    
    Args:
        args: Command line arguments
        
    Returns:
        Tuple containing:
        - List of FileStructure objects
        - CommonStructure containing common elements
    """
    # Parse .twb files
    structures = parse_directory(args.input_dir)
    
    if not structures:
        logger.error("No valid .twb files found, aborting")
        sys.exit(1)
    
    # Find commonalities
    common = find_commonalities(structures, args.threshold)
    
    return structures, common


def generate_outputs(
    structures: List[FileStructure],
    common: CommonStructure,
    args: argparse.Namespace
) -> None:
    """
    Generate all output files based on the analysis results.
    
    Args:
        structures: List of FileStructure objects
        common: CommonStructure containing common elements
        args: Command line arguments
    """
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate report
    if args.json:
        generate_json_report(common, len(structures), args.output_dir)
    else:
        generate_text_report(common, len(structures), args.output_dir)
    
    # Generate visualizations
    if not args.no_viz:
        viz_dir = os.path.join(args.output_dir, "visualizations")
        os.makedirs(viz_dir, exist_ok=True)
        
        # Generate common structure visualization
        common_viz_file = os.path.join(viz_dir, "common_structure")
        visualize_commonalities(common, common_viz_file, args.format)
        
        # Individual file visualizations removed as per user request
    
    # Generate mock .twb file
    if not args.no_mock:
        mock_file = os.path.join(args.output_dir, "common.twb")
        if args.placeholders:
            generate_mock_twb_with_placeholders(common, mock_file)
        else:
            generate_mock_twb(common, mock_file)


def generate_text_report(common: CommonStructure, total_files: int, output_dir: str) -> None:
    """
    Generate a text report of the analysis results.
    
    Args:
        common: CommonStructure containing common elements
        total_files: Total number of files analyzed
        output_dir: Directory for output files
    """
    report = get_stats_report(common, total_files)
    
    # Write report to file
    report_file = os.path.join(output_dir, "report.txt")
    with open(report_file, "w") as f:
        f.write(report)
    
    logger.info(f"Text report saved to {report_file}")
    
    # Print summary to console
    print("\n" + report)


def generate_json_report(common: CommonStructure, total_files: int, output_dir: str) -> None:
    """
    Generate a JSON report of the analysis results.
    
    Args:
        common: CommonStructure containing common elements
        total_files: Total number of files analyzed
        output_dir: Directory for output files
    """
    report_data = {
        "total_files": total_files,
        "common_paths": list(common.common_paths),
        "common_tags": common.common_tags,
        "path_frequency": {path: freq for path, freq in common.path_frequency.items()},
        "tag_frequency": {tag: freq for tag, freq in common.tag_frequency.items()}
    }
    
    # Write report to file
    report_file = os.path.join(output_dir, "report.json")
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)
    
    logger.info(f"JSON report saved to {report_file}")
    
    # Print summary to console
    print(f"\nAnalysis completed: {total_files} files processed")
    print(f"Found {len(common.common_paths)} common paths and {len(common.common_tags)} common tags")
    print(f"Detailed report saved to {report_file}")


def run_clustering(structures: List[FileStructure], args: argparse.Namespace) -> None:
    """
    Run clustering analysis on .twb files.
    
    Args:
        structures: List of FileStructure objects
        args: Command line arguments
    """
    logger.info("Starting clustering analysis")
    
    # Create clustering output directory
    cluster_dir = os.path.join(args.output_dir, "clusters")
    os.makedirs(cluster_dir, exist_ok=True)
    
    # Set output format to HTML for interactive visualization if not specified
    output_format = args.format.lower()
    if output_format not in ['html']:
        logger.info("Switching to HTML format for interactive cluster visualization")
        output_format = 'html'
    
    # Run clustering
    clusters, visualizations = cluster_xml_files(
        structures,
        n_clusters=args.n_clusters,
        method=args.cluster_method,
        output_dir=cluster_dir,
        output_format=output_format
    )
    
    # Generate report and common TWB file for each cluster
    for cluster_id, cluster_files in clusters.items():
        cluster_output_dir = os.path.join(cluster_dir, f"cluster_{cluster_id}")
        os.makedirs(cluster_output_dir, exist_ok=True)
        
        # Find commonalities within this cluster
        common = find_commonalities(cluster_files, args.threshold)
        
        # Generate report
        report_file = os.path.join(cluster_output_dir, "report.txt")
        with open(report_file, "w") as f:
            f.write(f"=== Cluster {cluster_id} Analysis ===\n\n")
            f.write(f"Total files in cluster: {len(cluster_files)}\n\n")
            f.write(f"Files in this cluster:\n")
            for structure in cluster_files:
                f.write(f"- {structure.filename}\n")
            f.write("\n")
            f.write(f"Common paths: {len(common.common_paths)}\n")
            f.write(f"Common tags: {len(common.common_tags)}\n")
        
        # Generate common TWB file for this cluster
        mock_file = os.path.join(cluster_output_dir, f"cluster_{cluster_id}_common.twb")
        if args.placeholders:
            generate_mock_twb_with_placeholders(common, mock_file)
        else:
            generate_mock_twb(common, mock_file)
        logger.info(f"Generated common TWB file for cluster {cluster_id}: {mock_file}")
    
    logger.info("Clustering analysis completed")
    
    # Print clustering summary
    print("\nClustering Results:")
    print(f"Method: {args.cluster_method}")
    print(f"Number of clusters: {args.n_clusters}")
    for cluster_id, cluster_files in clusters.items():
        print(f"  Cluster {cluster_id}: {len(cluster_files)} files")
    
    print("\nVisualization files:")
    for name, path in visualizations.items():
        print(f"  {name}: {path}")


def main():
    """Main entry point for the TwbCompare tool."""
    # Parse command line arguments
    args = parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting TwbCompare analysis")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Threshold: {args.threshold}")
    
    # Run analysis
    structures, common = run_analysis(args)
    
    # Always generate the common TWB file
    output_dir = os.path.join(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    mock_file = os.path.join(output_dir, "common.twb")
    if args.placeholders:
        generate_mock_twb_with_placeholders(common, mock_file)
    else:
        generate_mock_twb(common, mock_file)
    logger.info(f"Generated common TWB file: {mock_file}")
    
    # Always run clustering (regardless of --cluster flag)
    run_clustering(structures, args)
    
    logger.info("TwbCompare analysis completed successfully")


if __name__ == "__main__":
    main() 