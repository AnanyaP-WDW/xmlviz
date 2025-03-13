"""
Analyzer module for finding common elements and differences in TWB JSON files.
"""
import os
import json
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict


def extract_paths_and_tags(json_data: Dict[str, Any], 
                           current_path: str = "", 
                           paths: Optional[Set[str]] = None,
                           tags_with_attrs: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Tuple[Set[str], Dict[str, List[Dict[str, Any]]]]:
    """
    Extract all paths and tags with attributes from a JSON structure.
    
    Args:
        json_data: The JSON data to analyze
        current_path: Current path in the hierarchy
        paths: Set to collect all paths
        tags_with_attrs: Dict to collect all tags with their attributes
        
    Returns:
        Tuple of (all paths, all tags with attributes)
    """
    if paths is None:
        paths = set()
    if tags_with_attrs is None:
        tags_with_attrs = defaultdict(list)
    
    # Get the tag
    tag = json_data.get("tag", "")
    
    # Update current path
    if current_path:
        path = f"{current_path}/{tag}"
    else:
        path = tag
    
    # Add to paths
    if path:
        paths.add(path)
    
    # Add tag with attributes
    attrs = json_data.get("attributes", {})
    if attrs:
        tags_with_attrs[tag].append(attrs)
    else:
        tags_with_attrs[tag].append({})
    
    # Process children
    children = json_data.get("children", [])
    for child in children:
        extract_paths_and_tags(child, path, paths, tags_with_attrs)
    
    return paths, tags_with_attrs


def find_common_elements(json_files: List[str]) -> Dict[str, Any]:
    """
    Find common elements across all JSON files.
    
    Args:
        json_files: List of paths to JSON files
        
    Returns:
        Dictionary containing common paths and tags with attributes
    """
    all_file_paths: List[Set[str]] = []
    all_file_tags: List[Dict[str, List[Dict[str, Any]]]] = []
    
    # Process each file
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Extract paths and tags
        paths, tags_with_attrs = extract_paths_and_tags(json_data)
        all_file_paths.append(paths)
        all_file_tags.append(tags_with_attrs)
    
    # Find common paths (intersection of all sets)
    common_paths = set.intersection(*all_file_paths) if all_file_paths else set()
    
    # Find common tags with their attributes
    common_tags = {}
    
    if all_file_tags:
        # Get all unique tag names across all files
        all_tags = set()
        for file_tags in all_file_tags:
            all_tags.update(file_tags.keys())
        
        # For each tag, find attributes that appear in all files
        for tag in all_tags:
            # Check if this tag appears in all files
            if all(tag in file_tags for file_tags in all_file_tags):
                # Find common attributes for this tag
                common_attrs = {}
                for attr_name in set().union(*[
                    {attr_name for attrs_list in file_tags[tag] for attr_name in attrs_list.keys()}
                    for file_tags in all_file_tags
                ]):
                    # If attribute appears with same value in at least one instance in each file
                    values_by_file = []
                    for file_tags in all_file_tags:
                        file_values = set()
                        for attrs in file_tags[tag]:
                            if attr_name in attrs:
                                file_values.add(attrs[attr_name])
                        values_by_file.append(file_values)
                    
                    # If there's any value that appears in all files, consider it common
                    common_values = set.intersection(*[values for values in values_by_file if values])
                    if common_values:
                        # Just pick the first common value
                        common_attrs[attr_name] = next(iter(common_values))
                
                if common_attrs:
                    common_tags[tag] = common_attrs
    
    return {
        "common_paths": list(common_paths),
        "common_tags": common_tags
    }


def generate_diff(file_json: Dict[str, Any], common_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a diff between a file's JSON and the common JSON.
    
    Args:
        file_json: The JSON data for a specific file
        common_json: The common JSON data
        
    Returns:
        Dictionary containing differences
    """
    # Extract paths and tags from the file
    file_paths, file_tags_with_attrs = extract_paths_and_tags(file_json)
    
    # Get common paths and tags
    common_paths = set(common_json["common_paths"])
    common_tags = common_json["common_tags"]
    
    # Find unique paths in this file
    unique_paths = file_paths - common_paths
    
    # Find unique or different attributes for tags
    unique_tag_attrs = {}
    
    for tag, attrs_list in file_tags_with_attrs.items():
        # If tag isn't in common tags, all instances are unique
        if tag not in common_tags:
            unique_tag_attrs[tag] = attrs_list
            continue
        
        # For tags in common, check for different/additional attributes
        common_attrs = common_tags[tag]
        different_attrs_list = []
        
        for attrs in attrs_list:
            different_attrs = {}
            
            # Find attributes with different values or not in common
            for attr_name, attr_value in attrs.items():
                if attr_name not in common_attrs or common_attrs[attr_name] != attr_value:
                    different_attrs[attr_name] = attr_value
            
            if different_attrs:
                different_attrs_list.append(different_attrs)
        
        if different_attrs_list:
            unique_tag_attrs[tag] = different_attrs_list
    
    return {
        "unique_paths": list(unique_paths),
        "unique_tag_attributes": unique_tag_attrs
    }


def save_common_elements(common_elements: Dict[str, Any], output_dir: str) -> str:
    """
    Save common elements to a JSON file.
    
    Args:
        common_elements: Dictionary containing common elements
        output_dir: Directory to save the JSON file
        
    Returns:
        Path to the created JSON file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "common-twb.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(common_elements, f, indent=2)
    
    return output_path


def save_diff_files(json_files: List[str], common_json: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Generate and save diff files for each JSON file compared to common elements.
    
    Args:
        json_files: List of paths to JSON files
        common_json: Common elements dictionary
        output_dir: Directory to save diff files
        
    Returns:
        List of paths to created diff files
    """
    diff_files = []
    
    for json_file in json_files:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            file_json = json.load(f)
        
        # Generate diff
        diff = generate_diff(file_json, common_json)
        
        # Create diff filename
        base_name = os.path.basename(json_file)
        diff_filename = os.path.splitext(base_name)[0] + "-diff.json"
        diff_path = os.path.join(output_dir, diff_filename)
        
        # Save diff file
        with open(diff_path, 'w', encoding='utf-8') as f:
            json.dump(diff, f, indent=2)
        
        diff_files.append(diff_path)
    
    return diff_files 