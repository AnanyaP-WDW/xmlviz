"""
Parser module for converting Tableau .twb files (XML) to JSON.
"""
import os
import json
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET


def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    """
    Convert an XML element to a dictionary representation.
    
    Args:
        element: XML Element to convert
        
    Returns:
        Dictionary representation of the XML element
    """
    result: Dict[str, Any] = {}
    
    # Add tag name
    result["tag"] = element.tag
    
    # Add attributes if any
    if element.attrib:
        result["attributes"] = dict(element.attrib)
    
    # Add text content if any (stripped to handle whitespace)
    if element.text and element.text.strip():
        result["text"] = element.text.strip()
    
    # Process child elements
    children = list(element)
    if children:
        result["children"] = []
        for child in children:
            result["children"].append(xml_to_dict(child))
    
    return result


def parse_twb_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a Tableau .twb file and convert it to a dictionary.
    
    Args:
        file_path: Path to the .twb file
        
    Returns:
        Dictionary representation of the .twb file
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return xml_to_dict(root)
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML file {file_path}: {e}")


def convert_twb_to_json(twb_file_path: str, output_dir: str) -> str:
    """
    Convert a .twb file to JSON and save it to the output directory.
    
    Args:
        twb_file_path: Path to the .twb file
        output_dir: Directory to save the JSON file
        
    Returns:
        Path to the created JSON file
    """
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse TWB file
    twb_dict = parse_twb_file(twb_file_path)
    
    # Create output file path with .json extension
    base_name = os.path.basename(twb_file_path)
    json_filename = os.path.splitext(base_name)[0] + ".json"
    json_file_path = os.path.join(output_dir, json_filename)
    
    # Write to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(twb_dict, f, indent=2)
    
    return json_file_path


def convert_all_twb_files(input_dir: str, output_dir: str) -> List[str]:
    """
    Convert all .twb files in input_dir to JSON files in output_dir.
    
    Args:
        input_dir: Directory containing .twb files
        output_dir: Directory to save JSON files
        
    Returns:
        List of paths to created JSON files
    """
    json_files = []
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all .twb files
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.twb'):
            twb_path = os.path.join(input_dir, filename)
            json_path = convert_twb_to_json(twb_path, output_dir)
            json_files.append(json_path)
    
    return json_files 