"""
Generator module for creating mock Tableau .twb files.

This module provides functionality to generate a mock .twb file
based on the common structure found across multiple .twb files.
"""
import os
import logging
from typing import Dict, List, Set, Optional
from lxml import etree

from twbcompare.models import CommonStructure

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_mock_twb(common: CommonStructure, output_file: str) -> str:
    """
    Generate a mock .twb file based on the common structure.
    
    Args:
        common: CommonStructure containing common elements
        output_file: Path to the output file
        
    Returns:
        Path to the generated file, or empty string on error
    """
    logger.info(f"Generating mock .twb file: {output_file}")
    
    try:
        # Create the XML tree
        root = _build_xml_tree(common)
        
        # Create the ElementTree and write to file
        tree = etree.ElementTree(root)
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        tree.write(
            output_file,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )
        
        logger.info(f"Mock .twb file generated successfully: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Error generating mock .twb file: {e}")
        return ""


def _build_xml_tree(common: CommonStructure) -> etree._Element:
    """
    Build an XML tree based on the common structure.
    
    Args:
        common: CommonStructure containing common elements
        
    Returns:
        lxml Element representing the root of the XML tree
    """
    # Start with an empty dictionary of elements
    elements: Dict[str, etree._Element] = {}
    
    # Sort paths to ensure parent paths are processed before children
    sorted_paths = sorted(common.common_paths)
    
    for path in sorted_paths:
        # Skip empty paths
        if not path:
            continue
        
        # Split the path into components
        parts = path.strip("/").split("/")
        tag_name = parts[-1]
        
        # Create this element
        if path not in elements:
            # Determine attributes for this tag
            attrs = {}
            if tag_name in common.common_tags:
                attrs = common.common_tags[tag_name][0]
            
            # Create the element
            element = etree.Element(tag_name, attrib=attrs)
            elements[path] = element
            
            # If this is not the root, add it to its parent
            if len(parts) > 1:
                parent_path = "/" + "/".join(parts[:-1])
                if parent_path in elements:
                    elements[parent_path].append(element)
    
    # Return the root element
    root_path = None
    for path in sorted_paths:
        parts = path.strip("/").split("/")
        if len(parts) == 1:
            root_path = path
            break
    
    if root_path and root_path in elements:
        return elements[root_path]
    else:
        # If no root was found, create a default workbook root
        logger.warning("No root element found in common paths, creating default workbook root")
        return etree.Element("workbook")


def generate_mock_twb_with_placeholders(
    common: CommonStructure, 
    output_file: str,
    placeholder_values: Dict[str, str] = None
) -> str:
    """
    Generate a mock .twb file with placeholder values for empty attributes.
    
    Args:
        common: CommonStructure containing common elements
        output_file: Path to the output file
        placeholder_values: Optional dictionary mapping attribute names to placeholder values
        
    Returns:
        Path to the generated file, or empty string on error
    """
    if placeholder_values is None:
        placeholder_values = {
            "name": "PlaceholderName",
            "caption": "PlaceholderCaption",
            "id": "PlaceholderID",
            "value": "PlaceholderValue"
        }
    
    logger.info(f"Generating mock .twb file with placeholders: {output_file}")
    
    # Create a copy of the common structure with placeholder values
    modified_common = CommonStructure()
    modified_common.common_paths = common.common_paths.copy()
    modified_common.path_frequency = common.path_frequency.copy()
    modified_common.tag_frequency = common.tag_frequency.copy()
    
    # Update attributes with placeholders
    modified_common.common_tags = {}
    for tag, attrs_list in common.common_tags.items():
        modified_attrs = [{} for _ in attrs_list]
        
        for i, attrs in enumerate(attrs_list):
            for attr_name, attr_value in attrs.items():
                if not attr_value and attr_name in placeholder_values:
                    modified_attrs[i][attr_name] = placeholder_values[attr_name]
                else:
                    modified_attrs[i][attr_name] = attr_value
        
        modified_common.common_tags[tag] = modified_attrs
    
    # Generate the mock .twb file
    return generate_mock_twb(modified_common, output_file) 