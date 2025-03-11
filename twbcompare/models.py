"""
Data models for storing XML tag structures and commonalities.

This module defines the core data structures used throughout the TwbCompare tool:
- TagNode: Represents an XML tag and its hierarchy
- FileStructure: Represents the structure of a single .twb file
- CommonStructure: Represents common elements across multiple .twb files
"""
from typing import Dict, List, Set, Optional


class TagNode:
    """
    Represents an XML tag with its attributes, path, and child nodes.
    
    Attributes:
        tag_name (str): The name of the XML tag
        attributes (Dict[str, str]): Key-value pairs of tag attributes
        path (str): Full hierarchy path (e.g., /workbook/worksheet)
        children (List[TagNode]): Child tags
    """
    def __init__(self, tag_name: str, attributes: Dict[str, str], path: str):
        self.tag_name = tag_name
        self.attributes = attributes
        self.path = path
        self.children: List[TagNode] = []
    
    def __repr__(self) -> str:
        attr_str = ", ".join(f"{k}={v}" for k, v in self.attributes.items())
        return f"TagNode({self.tag_name}, [{attr_str}], {self.path}, {len(self.children)} children)"


class FileStructure:
    """
    Represents the complete structure of a .twb file.
    
    Attributes:
        filename (str): Name of the source file
        root (TagNode): Root node of the XML tree
        all_paths (Set[str]): Set of all unique paths in the structure
        all_tags (Dict[str, List[Dict[str, str]]]): Dictionary mapping tag names to lists of attribute dictionaries
    """
    def __init__(self, filename: str, root: TagNode):
        self.filename = filename
        self.root = root
        self.all_paths: Set[str] = set()
        self.all_tags: Dict[str, List[Dict[str, str]]] = {}
        
        # Populate all_paths and all_tags from the root node
        self._collect_data(self.root)
    
    def _collect_data(self, node: TagNode) -> None:
        """Recursively collect paths and tags from the node and its children."""
        self.all_paths.add(node.path)
        
        if node.tag_name not in self.all_tags:
            self.all_tags[node.tag_name] = []
        self.all_tags[node.tag_name].append(node.attributes)
        
        for child in node.children:
            self._collect_data(child)


class CommonStructure:
    """
    Represents the common elements across multiple .twb files.
    
    Attributes:
        common_paths (Set[str]): Paths present in all analyzed files
        common_tags (Dict[str, List[Dict[str, str]]]): Tags with their common attributes
        path_frequency (Dict[str, float]): Frequency of paths across files (as percentage)
        tag_frequency (Dict[str, float]): Frequency of tags across files (as percentage)
    """
    def __init__(self):
        self.common_paths: Set[str] = set()
        self.common_tags: Dict[str, List[Dict[str, str]]] = {}
        self.path_frequency: Dict[str, float] = {}
        self.tag_frequency: Dict[str, float] = {}
    
    def __repr__(self) -> str:
        return f"CommonStructure(paths={len(self.common_paths)}, tags={len(self.common_tags)})" 