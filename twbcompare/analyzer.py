"""
Analyzer module for comparing Tableau .twb files and finding commonalities.

This module provides functionality to analyze multiple FileStructure objects
and identify common elements across them, such as tags, attributes, and paths.
"""
import logging
from typing import List, Dict, Set, Tuple
from collections import Counter

from twbcompare.models import FileStructure, CommonStructure

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_commonalities(structures: List[FileStructure], threshold: float = 1.0) -> CommonStructure:
    """
    Find common elements across multiple .twb file structures.
    
    Args:
        structures: List of FileStructure objects to analyze
        threshold: Minimum frequency threshold (0.0-1.0) for considering elements common.
                   Default is 1.0 (100% - must be in all files)
    
    Returns:
        CommonStructure object containing the common elements
    """
    if not structures:
        logger.warning("No structures provided for analysis")
        return CommonStructure()
    
    logger.info(f"Analyzing commonalities across {len(structures)} files with threshold {threshold}")
    
    common = CommonStructure()
    
    # Analyze paths
    common.common_paths, common.path_frequency = _find_common_paths(structures, threshold)
    
    # Analyze tags and their attributes
    common.common_tags, common.tag_frequency = _find_common_tags_and_attributes(structures, threshold)
    
    logger.info(f"Found {len(common.common_paths)} common paths and {len(common.common_tags)} common tags")
    
    return common


def _find_common_paths(structures: List[FileStructure], threshold: float) -> Tuple[Set[str], Dict[str, float]]:
    """
    Find common paths across file structures.
    
    Args:
        structures: List of FileStructure objects
        threshold: Minimum frequency threshold
        
    Returns:
        Tuple containing:
        - Set of common paths
        - Dictionary mapping paths to their frequency
    """
    # Collect all unique paths
    all_paths = set()
    for structure in structures:
        all_paths.update(structure.all_paths)
    
    # Count occurrences of each path
    path_counts = Counter()
    for structure in structures:
        path_counts.update(structure.all_paths)
    
    # Calculate frequency as percentage
    total_files = len(structures)
    path_frequency = {path: count / total_files for path, count in path_counts.items()}
    
    # Filter by threshold
    common_paths = {path for path, freq in path_frequency.items() if freq >= threshold}
    
    return common_paths, path_frequency


def _find_common_tags_and_attributes(
    structures: List[FileStructure], threshold: float
) -> Tuple[Dict[str, List[Dict[str, str]]], Dict[str, float]]:
    """
    Find common tags and attributes across file structures.
    
    Args:
        structures: List of FileStructure objects
        threshold: Minimum frequency threshold
        
    Returns:
        Tuple containing:
        - Dictionary mapping common tags to lists of attribute dictionaries
        - Dictionary mapping tags to their frequency
    """
    # Collect all unique tags
    all_tags = set()
    for structure in structures:
        all_tags.update(structure.all_tags.keys())
    
    # Count occurrences of each tag
    tag_counts = Counter()
    for structure in structures:
        tag_counts.update(structure.all_tags.keys())
    
    # Calculate frequency as percentage
    total_files = len(structures)
    tag_frequency = {tag: count / total_files for tag, count in tag_counts.items()}
    
    # Filter tags by threshold
    common_tags = {tag for tag, freq in tag_frequency.items() if freq >= threshold}
    
    # Find common attributes for each common tag
    common_tags_with_attrs = {}
    for tag in common_tags:
        # Collect all attribute keys for this tag
        attr_keys = set()
        for structure in structures:
            if tag in structure.all_tags:
                for attrs in structure.all_tags[tag]:
                    attr_keys.update(attrs.keys())
        
        # Count occurrences of each attribute
        attr_counts = {key: 0 for key in attr_keys}
        for structure in structures:
            if tag in structure.all_tags:
                # For each instance of this tag in the structure
                for attrs in structure.all_tags[tag]:
                    for key in attrs:
                        attr_counts[key] += 1
        
        # Filter attributes by threshold
        common_attrs = {key: "" for key, count in attr_counts.items() 
                        if count / total_files >= threshold}
        
        if common_attrs:
            common_tags_with_attrs[tag] = [common_attrs]
    
    return common_tags_with_attrs, tag_frequency


def get_stats_report(common: CommonStructure, total_files: int) -> str:
    """
    Generate a text report of commonality statistics.
    
    Args:
        common: CommonStructure containing analysis results
        total_files: Total number of files analyzed
        
    Returns:
        Formatted string with statistics
    """
    report = []
    report.append(f"Commonality Analysis Report ({total_files} files)")
    report.append("=" * 40)
    
    # Common paths
    report.append("\nCommon Hierarchy Paths:")
    for path in sorted(common.common_paths):
        freq = common.path_frequency[path] * 100
        report.append(f"  {path} ({freq:.1f}%)")
    
    # Common tags with attributes
    report.append("\nCommon Tags with Attributes:")
    for tag, attrs_list in sorted(common.common_tags.items()):
        freq = common.tag_frequency[tag] * 100
        attrs_str = ", ".join(f"{k}={v}" for k, v in attrs_list[0].items())
        report.append(f"  {tag} ({freq:.1f}%): [{attrs_str}]")
    
    return "\n".join(report) 