"""
Visualizer module for generating graphical representations of .twb structures.

This module uses Graphviz to generate tree diagrams of .twb file structures,
visualizing the tags, attributes, and hierarchy, as well as commonalities.
"""
import os
import logging
from typing import Set, Dict, Optional, Tuple
import graphviz

from twbcompare.models import FileStructure, TagNode, CommonStructure

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
    Generate a visual representation of a FileStructure.
    
    Args:
        structure: FileStructure to visualize
        output_file: Base name for the output file (without extension)
        highlight_paths: Optional set of paths to highlight
        output_format: Output format (png or svg)
        
    Returns:
        Path to the generated visualization file
    """
    logger.info(f"Generating visualization for {structure.filename}")
    
    # Create a new Graphviz Digraph
    dot = graphviz.Digraph(
        comment=f"Hierarchy for {structure.filename}",
        format=output_format,
        engine='dot'
    )
    
    # Set graph attributes
    dot.attr('graph', rankdir='TB', splines='ortho')
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
    
    # Keep track of nodes that have been added
    nodes_added = set()
    
    # Process the TagNode hierarchy recursively
    _add_node_to_graph(dot, structure.root, nodes_added, highlight_paths)
    
    # Render the graph to a file
    try:
        output_path = dot.render(filename=output_file, cleanup=True)
        logger.info(f"Visualization saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error rendering visualization: {e}")
        return ""


def _add_node_to_graph(
    dot: graphviz.Digraph, 
    node: TagNode, 
    nodes_added: Set[str],
    highlight_paths: Optional[Set[str]] = None
) -> None:
    """
    Recursively add a TagNode and its children to the graph.
    
    Args:
        dot: Graphviz Digraph object
        node: TagNode to add
        nodes_added: Set of node IDs that have been added
        highlight_paths: Optional set of paths to highlight
    """
    # Create a unique ID for this node
    node_id = node.path
    
    # Format the node label
    attr_str = ", ".join(f"{k}={v}" for k, v in node.attributes.items())
    label = f"{node.tag_name}"
    if attr_str:
        label += f" [{attr_str}]"
    
    # Determine node color based on highlighting
    node_attrs = {}
    if highlight_paths and node.path in highlight_paths:
        node_attrs['fillcolor'] = 'lightgreen'
    
    # Add the node if not already added
    if node_id not in nodes_added:
        dot.node(node_id, label, **node_attrs)
        nodes_added.add(node_id)
    
    # Add edges and process children
    for child in node.children:
        child_id = child.path
        
        # Add the child recursively
        _add_node_to_graph(dot, child, nodes_added, highlight_paths)
        
        # Add the edge
        dot.edge(node_id, child_id)


def visualize_commonalities(
    common: CommonStructure, 
    output_file: str,
    output_format: str = "png"
) -> str:
    """
    Generate a visualization of common elements across .twb files.
    
    Args:
        common: CommonStructure containing common elements
        output_file: Base name for the output file (without extension)
        output_format: Output format (png or svg)
        
    Returns:
        Path to the generated visualization file
    """
    logger.info("Generating visualization of common elements")
    
    # Create a new Graphviz Digraph
    dot = graphviz.Digraph(
        comment="Common .twb Structure",
        format=output_format,
        engine='dot'
    )
    
    # Set graph attributes
    dot.attr('graph', rankdir='TB', splines='ortho')
    dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
    
    # Track nodes that have been added
    nodes_added = set()
    
    # Add all common paths as nodes
    for path in sorted(common.common_paths):
        # Split the path into components
        parts = path.strip("/").split("/")
        
        for i in range(len(parts)):
            # Create parent and child paths
            parent_path = "/" + "/".join(parts[:i]) if i > 0 else ""
            child_path = "/" + "/".join(parts[:i+1])
            
            # Add the child node if not already added
            if child_path not in nodes_added:
                tag_name = parts[i]
                
                # Determine if this tag has common attributes
                label = tag_name
                if tag_name in common.common_tags:
                    attrs = common.common_tags[tag_name][0]
                    if attrs:
                        attr_str = ", ".join(f"{k}={v}" for k, v in attrs.items())
                        label += f" [{attr_str}]"
                
                # Add frequency information to the label
                if child_path in common.path_frequency:
                    freq = common.path_frequency[child_path] * 100
                    label += f" ({freq:.1f}%)"
                
                dot.node(child_path, label)
                nodes_added.add(child_path)
            
            # Add the edge if parent exists
            if i > 0 and parent_path in nodes_added:
                dot.edge(parent_path, child_path)
    
    # Render the graph to a file
    try:
        output_path = dot.render(filename=output_file, cleanup=True)
        logger.info(f"Common structure visualization saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error rendering visualization: {e}")
        return ""


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