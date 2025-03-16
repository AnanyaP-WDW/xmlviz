"""
XML Analyzer module for finding common elements and differences in TWB (XML) files.
"""
import os
import copy
from typing import Dict, Any, List, Set, Tuple, Optional
import xml.etree.ElementTree as ET
from collections import defaultdict
from lxml import etree


def normalize_element(element: ET.Element) -> ET.Element:
    """
    Normalize an XML element by sorting attributes and children to ensure consistent comparison.
    
    Args:
        element: XML Element to normalize
        
    Returns:
        Normalized copy of the XML element
    """
    # Create a deep copy to avoid modifying the original
    normalized = copy.deepcopy(element)
    
    # Sort attributes
    if hasattr(normalized, 'attrib') and normalized.attrib:
        # Sort children by tag and attributes
        for child in normalized:
            normalize_element(child)
    
    return normalized


def element_signature(element: ET.Element) -> Tuple[str, frozenset]:
    """
    Create a unique signature for an element based on its tag and attributes.
    
    Args:
        element: XML Element
        
    Returns:
        Tuple of (tag name, frozenset of attribute items)
    """
    if hasattr(element, 'attrib') and element.attrib:
        return (element.tag, frozenset(element.attrib.items()))
    return (element.tag, frozenset())


def compare_elements(elem1: ET.Element, elem2: ET.Element) -> bool:
    """
    Compare two XML elements for equality of tag and attributes.
    
    Args:
        elem1: First XML element
        elem2: Second XML element
        
    Returns:
        True if elements have same tag and attributes
    """
    if elem1.tag != elem2.tag:
        return False
    
    # Compare attributes
    return elem1.attrib == elem2.attrib


def collect_element_frequencies(xml_trees: List[ET.ElementTree]) -> Dict[Tuple[str, frozenset], int]:
    """
    Collect frequency statistics for elements across all XML trees.
    
    Args:
        xml_trees: List of XML ElementTree objects
        
    Returns:
        Dictionary mapping element signatures to their frequency counts
    """
    element_counts = defaultdict(int)
    
    # Process each tree
    for tree in xml_trees:
        root = tree.getroot()
        _collect_element_recursive(root, element_counts)
    
    return element_counts


def _collect_element_recursive(element: ET.Element, counts: Dict[Tuple[str, frozenset], int]) -> None:
    """
    Recursively collect element frequency statistics.
    
    Args:
        element: Current XML element
        counts: Dictionary to store counts
    """
    # Count this element
    sig = element_signature(element)
    counts[sig] += 1
    
    # Process all children
    for child in element:
        _collect_element_recursive(child, counts)


def find_common_structure(xml_trees: List[ET.ElementTree], threshold: float = 1.0) -> Optional[ET.Element]:
    """
    Find the common structure across all XML trees.
    
    Args:
        xml_trees: List of XML ElementTree objects
        threshold: Proportion (0.0-1.0) of trees that must contain an element for it to be considered common
        
    Returns:
        Element representing the common structure, or None if none exists
    """
    if not xml_trees:
        return None
    
    # Calculate the required count based on threshold
    total_trees = len(xml_trees)
    required_count = max(1, int(threshold * total_trees))
    
    # First pass: collect frequency statistics
    element_counts = collect_element_frequencies(xml_trees)
    
    # Start with the first tree as the base
    base_root = xml_trees[0].getroot()
    common_root = copy.deepcopy(base_root)
    
    # Second pass: compare with each other tree
    for tree in xml_trees[1:]:
        root = tree.getroot()
        
        # If roots have different tags, no common structure
        if common_root.tag != root.tag:
            return ET.Element("workbook")  # Return a minimal common root
        
        # Find common attributes
        common_attrs = {}
        for key, value in common_root.attrib.items():
            if key in root.attrib and root.attrib[key] == value:
                common_attrs[key] = value
        
        # Update common root attributes
        common_root.attrib.clear()
        for key, value in common_attrs.items():
            common_root.attrib[key] = value
        
        # Process children recursively with frequency information
        common_root = process_children_recursively_with_counts(common_root, root, element_counts, required_count)
    
    return common_root


def process_children_recursively_with_counts(common_elem: ET.Element, compare_elem: ET.Element, 
                                            element_counts: Dict[Tuple[str, frozenset], int],
                                            required_count: int) -> ET.Element:
    """
    Process children of elements recursively to find common structure using frequency counts.
    
    Args:
        common_elem: Current common element being built
        compare_elem: Element to compare against
        element_counts: Dictionary of element frequency counts
        required_count: Minimum number of trees required to keep an element
        
    Returns:
        Updated common element with only common children/structure
    """
    # Create a new element with same tag and common attributes
    new_common = ET.Element(common_elem.tag)
    
    # Add common attributes
    for key, value in common_elem.attrib.items():
        if key in compare_elem.attrib and compare_elem.attrib[key] == value:
            new_common.attrib[key] = value
    
    # Map children by their signature for efficient lookup
    compare_children_map = {}
    for child in compare_elem:
        sig = element_signature(child)
        if sig not in compare_children_map:
            compare_children_map[sig] = []
        compare_children_map[sig].append(child)
    
    # Process each child of the common element
    for common_child in common_elem:
        common_sig = element_signature(common_child)
        
        # Check if this element meets the threshold requirement
        if element_counts[common_sig] >= required_count:
            # If this signature exists in compare element
            if common_sig in compare_children_map and compare_children_map[common_sig]:
                # Get a matching child (and remove it to handle duplicates)
                compare_child = compare_children_map[common_sig].pop(0)
                
                # Recursively process this child
                new_child = process_children_recursively_with_counts(
                    common_child, compare_child, element_counts, required_count
                )
                
                # Only add if the child has any content (tag, attributes, or sub-elements)
                if new_child.tag or new_child.attrib or len(new_child) > 0:
                    new_common.append(new_child)
            else:
                # Element is not in this file but meets the threshold overall
                new_common.append(copy.deepcopy(common_child))
    
    return new_common


def generate_xml_diff(original: ET.Element, common: ET.Element) -> ET.Element:
    """
    Generate an XML element representing the differences between original and common.
    
    Args:
        original: Original XML element
        common: Common XML element
        
    Returns:
        XML element containing differences
    """
    # Create diff element with same tag
    diff = ET.Element(original.tag)
    
    # Add attributes that are different or only in original
    for key, value in original.attrib.items():
        if key not in common.attrib or common.attrib[key] != value:
            diff.attrib[key] = value
    
    # Map common children by signature for efficient lookup
    common_children_map = {}
    for child in common:
        sig = element_signature(child)
        if sig not in common_children_map:
            common_children_map[sig] = []
        common_children_map[sig].append(child)
    
    # Process children
    for orig_child in original:
        orig_sig = element_signature(orig_child)
        
        # If this signature exists in common structure
        if orig_sig in common_children_map and common_children_map[orig_sig]:
            # Get a matching child (and remove it to handle duplicates)
            common_child = common_children_map[orig_sig].pop(0)
            
            # Recursively get differences
            child_diff = generate_xml_diff(orig_child, common_child)
            
            # Only add if there are differences
            if child_diff.attrib or len(child_diff) > 0:
                diff.append(child_diff)
        else:
            # Child doesn't exist in common, so it's unique to original
            diff.append(copy.deepcopy(orig_child))
    
    return diff


def parse_all_twb_files(input_dir: str) -> List[ET.ElementTree]:
    """
    Parse all TWB files in the input directory.
    
    Args:
        input_dir: Directory containing TWB files
        
    Returns:
        List of parsed ElementTree objects
    """
    xml_trees = []
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.twb'):
            file_path = os.path.join(input_dir, filename)
            try:
                tree = ET.parse(file_path)
                xml_trees.append(tree)
            except ET.ParseError as e:
                print(f"Error parsing {file_path}: {e}")
    
    return xml_trees


def save_xml_tree(root: ET.Element, file_path: str) -> str:
    """
    Save an XML element tree to a file with proper formatting.
    
    Args:
        root: Root XML element to save
        file_path: Path to save the XML file
        
    Returns:
        Path to the saved file
    """
    # Convert ElementTree element to lxml for pretty printing
    xml_string = ET.tostring(root, encoding='unicode')
    parser = etree.XMLParser(remove_blank_text=True)
    lxml_root = etree.fromstring(xml_string, parser)
    
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save with pretty formatting
    tree = etree.ElementTree(lxml_root)
    tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    
    return file_path


def find_common_twb_structure(input_dir: str, output_dir: str, threshold: float = 1.0) -> Tuple[str, List[str]]:
    """
    Find the common structure across all TWB files and generate diff files.
    
    Args:
        input_dir: Directory containing TWB files
        output_dir: Directory to save results
        threshold: Proportion (0.0-1.0) of files that must contain an element for it to be considered common
        
    Returns:
        Tuple of (path to common XML file, list of paths to diff files)
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse all TWB files
    xml_trees = parse_all_twb_files(input_dir)
    
    if not xml_trees:
        raise ValueError(f"No valid TWB files found in {input_dir}")
    
    # Find common structure with threshold
    common_root = find_common_structure(xml_trees, threshold)
    
    # Save common structure
    common_file_path = os.path.join(output_dir, "common-twb.xml")
    save_xml_tree(common_root, common_file_path)
    
    # Get list of original TWB filenames
    original_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.twb')]
    
    # Generate and save diff files
    diff_files = []
    
    for i, tree in enumerate(xml_trees):
        original_root = tree.getroot()
        
        # Generate diff
        diff_root = generate_xml_diff(original_root, common_root)
        
        # Get original filename
        if i < len(original_files):
            original_filename = original_files[i]
            base_name = os.path.splitext(original_filename)[0]
            diff_filename = f"{base_name}-diff.xml"
            
            # Save diff
            diff_path = os.path.join(output_dir, diff_filename)
            save_xml_tree(diff_root, diff_path)
            diff_files.append(diff_path)
    
    return common_file_path, diff_files 