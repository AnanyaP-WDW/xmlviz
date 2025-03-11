"""
TwbCompare - A Python-based tool for analyzing, comparing, and visualizing Tableau .twb files.

This package provides functionality to:
- Parse and analyze multiple .twb files (XML format)
- Identify common elements across files (tags, attributes, hierarchy)
- Visualize the structure and commonalities
- Generate a mock .twb file based on common elements
- Cluster XML files based on structural similarity
"""

__version__ = "0.1.0"
__author__ = "TwbCompare Team"

from twbcompare.models import TagNode, FileStructure, CommonStructure
from twbcompare.parser import parse_twb, parse_directory
from twbcompare.analyzer import find_commonalities, get_stats_report
from twbcompare.matplotlib_visualizer import visualize_structure, visualize_commonalities
from twbcompare.generator import generate_mock_twb, generate_mock_twb_with_placeholders
from twbcompare.clustering import cluster_xml_files, XMLClusterAnalyzer 