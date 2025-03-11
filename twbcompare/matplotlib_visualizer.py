"""
Matplotlib-based visualizer module for TwbCompare.

This module provides visualization of .twb structures and commonalities
using Matplotlib instead of Graphviz.
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import networkx as nx
from typing import Dict, List, Set, Optional, Tuple

from twbcompare.models import TagNode, FileStructure, CommonStructure

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def visualize_structure(
    structure: FileStructure,
    output_file: str,
    highlight_paths: Optional[Set[str]] = None,
    output_format: str = "png"
) -> str:
    """
    Generate a visual representation of a FileStructure using Matplotlib.
    
    Args:
        structure: FileStructure to visualize
        output_file: Base name for the output file (without extension)
        highlight_paths: Optional set of paths to highlight
        output_format: Output format (png or svg)
        
    Returns:
        Path to the generated visualization file
    """
    logger.info(f"Generating matplotlib visualization for {structure.filename}")
    
    G = nx.DiGraph()
    nodes_added = set()
    
    # Add nodes and edges
    for path in sorted(structure.all_paths):
        parts = path.strip("/").split("/")
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            child = "/".join(parts[:i+1])
            
            if child not in nodes_added:
                label = parts[i]
                # Add attributes if available
                tag = parts[i]
                if tag in structure.all_tags:
                    attrs = structure.all_tags[tag][0]  # Just use the first instance for simplicity
                    if attrs:
                        label += f"\n{str(attrs)}"
                G.add_node(child, label=label)
                nodes_added.add(child)
            
            if i > 0:
                G.add_edge(parent, child)
    
    # Generate the visualization
    plt.figure(figsize=(14, 10))
    
    # Use a built-in layout algorithm instead of graphviz_layout
    pos = hierarchy_pos(G)
    
    # Draw nodes
    node_colors = []
    for node in G.nodes():
        if highlight_paths and node in highlight_paths:
            node_colors.append('lightgreen')
        else:
            node_colors.append('lightblue')
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    
    # Add labels with smaller font size and wrapping
    labels = nx.get_node_attributes(G, 'label')
    wrapped_labels = {node: wrap_text(label, 20) for node, label in labels.items()}
    nx.draw_networkx_labels(G, pos, labels=wrapped_labels, font_size=8)
    
    # Adjust layout
    plt.axis('off')
    plt.title(f"Structure of {structure.filename}")
    plt.tight_layout()
    
    # Save the figure
    output_path = f"{output_file}.{output_format}"
    plt.savefig(output_path, format=output_format, dpi=300)
    plt.close()
    
    logger.info(f"Visualization saved to {output_path}")
    return output_path


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Custom function for positioning nodes in a hierarchical layout.
    This is a replacement for graphviz_layout.
    
    G: the graph
    root: the root node of current branch (optional)
    width: horizontal space allocated for this branch (optional)
    vert_gap: gap between levels of hierarchy (optional)
    vert_loc: vertical location of root (optional)
    xcenter: horizontal location of root (optional)
    """
    if root is None:
        if isinstance(G, nx.DiGraph):
            roots = [v for v, d in G.in_degree() if d == 0]
        else:
            roots = [0]
        if len(roots) > 1:
            root = roots[0]  # Choose the first root if multiple roots
        else:
            root = roots[0]
    
    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph):
            if parent is not None:
                children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                    vert_loc=vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent=root, parsed=parsed)
        return pos
    
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def wrap_text(text, width):
    """Wrap text to fit in the node visualization."""
    if not isinstance(text, str):
        return str(text)
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # If the word is too long for the width, split it
                current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def visualize_commonalities(
    common: CommonStructure,
    output_file: str,
    output_format: str = "png"
) -> str:
    """
    Generate a visualization of common elements using Matplotlib.
    
    Args:
        common: CommonStructure containing common elements
        output_file: Base name for the output file (without extension)
        output_format: Output format (png or svg)
        
    Returns:
        Path to the generated visualization file
    """
    logger.info("Generating matplotlib visualization of common elements")
    
    G = nx.DiGraph()
    nodes_added = set()
    
    # Add nodes and edges
    for path in sorted(common.common_paths):
        parts = path.strip("/").split("/")
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            child = "/".join(parts[:i+1])
            
            if child not in nodes_added:
                label = parts[i]
                # Add attributes if available
                tag = parts[i]
                if tag in common.common_tags:
                    attrs = common.common_tags[tag][0]
                    if attrs:
                        label += f"\n{str(attrs)}"
                G.add_node(child, label=label)
                nodes_added.add(child)
            
            if i > 0:
                G.add_edge(parent, child)
    
    # Generate the visualization
    plt.figure(figsize=(14, 10))
    
    # Use a built-in layout algorithm instead of graphviz_layout
    pos = hierarchy_pos(G)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="lightgreen", alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    
    # Add labels with smaller font size and wrapping
    labels = nx.get_node_attributes(G, 'label')
    wrapped_labels = {node: wrap_text(label, 20) for node, label in labels.items()}
    nx.draw_networkx_labels(G, pos, labels=wrapped_labels, font_size=8)
    
    # Adjust layout
    plt.axis('off')
    plt.title("Common Elements Across All .twb Files")
    plt.tight_layout()
    
    # Save the figure
    output_path = f"{output_file}.{output_format}"
    plt.savefig(output_path, format=output_format, dpi=300)
    plt.close()
    
    logger.info(f"Common structure visualization saved to {output_path}")
    return output_path


def visualize_file_structure(
    structure: FileStructure,
    common: CommonStructure,
    output_dir: str,
    output_format: str = "png"
) -> str:
    """
    Generate a visualization of a file structure, highlighting common elements.
    
    Args:
        structure: FileStructure to visualize
        common: CommonStructure containing common elements to highlight
        output_dir: Directory for output files
        output_format: Output format (png or svg)
        
    Returns:
        Path to the generated visualization file
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{structure.filename}_structure")
    
    return visualize_structure(
        structure,
        output_file,
        highlight_paths=common.common_paths,
        output_format=output_format
    ) 