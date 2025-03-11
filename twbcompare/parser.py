"""
Parser module for analyzing Tableau .twb files (XML).

This module provides functionality to parse .twb files and extract their structure,
including tags, attributes, and hierarchy.
"""
import os
import logging
from typing import Optional, List
from lxml import etree

from twbcompare.models import TagNode, FileStructure

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_twb(file_path: str) -> Optional[FileStructure]:
    """
    Parse a Tableau .twb file and build a FileStructure object.
    
    Args:
        file_path: Path to the .twb file
        
    Returns:
        FileStructure object if parsing is successful, None otherwise
    """
    filename = os.path.basename(file_path)
    
    try:
        logger.info(f"Parsing file: {filename}")
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Build the tag hierarchy
        root_node = _build_tag_node(root)
        
        # Create and return the FileStructure
        return FileStructure(filename, root_node)
    
    except etree.XMLSyntaxError as e:
        logger.error(f"XML syntax error in {filename}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        return None


def _build_tag_node(xml_element, current_path: str = "") -> TagNode:
    """
    Recursively build a TagNode hierarchy from an XML element.
    
    Args:
        xml_element: lxml Element object
        current_path: Current path in the hierarchy
        
    Returns:
        TagNode representing the XML element and its children
    """
    # Extract the tag name
    tag_name = xml_element.tag
    
    # Build the full path
    path = f"{current_path}/{tag_name}" if current_path else f"/{tag_name}"
    
    # Create a TagNode for this element
    node = TagNode(tag_name, dict(xml_element.attrib), path)
    
    # Process children
    for child in xml_element:
        if isinstance(child.tag, str):  # Skip comments, processing instructions, etc.
            child_node = _build_tag_node(child, path)
            node.children.append(child_node)
    
    return node


def parse_directory(directory_path: str) -> List[FileStructure]:
    """
    Parse all .twb files in the given directory.
    
    Args:
        directory_path: Path to directory containing .twb files
        
    Returns:
        List of FileStructure objects
    """
    structures = []
    
    try:
        files = [f for f in os.listdir(directory_path) if f.endswith(".twb")]
        logger.info(f"Found {len(files)} .twb files in {directory_path}")
        
        for file in files:
            file_path = os.path.join(directory_path, file)
            structure = parse_twb(file_path)
            if structure:
                structures.append(structure)
        
        logger.info(f"Successfully parsed {len(structures)} out of {len(files)} files")
        return structures
    
    except Exception as e:
        logger.error(f"Error parsing directory {directory_path}: {e}")
        return structures 