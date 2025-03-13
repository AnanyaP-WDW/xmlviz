#!/usr/bin/env python
"""
Test script for the XML analyzer functionality.

Usage:
    python test_xml_analyzer.py /path/to/twb/files [--output-dir output_dir]
"""
import os
import sys
import argparse
from twbcompare.utils.xml_analyzer import (
    parse_all_twb_files,
    find_common_structure,
    save_xml_tree,
    generate_xml_diff
)

def main():
    """Main entry point for the test script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test XML analyzer functionality")
    parser.add_argument("input_dir", help="Directory containing .twb files to analyze")
    parser.add_argument("--output-dir", default="test_results", help="Directory to save results")
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        print(f"Parsing TWB files from {args.input_dir}...")
        xml_trees = parse_all_twb_files(args.input_dir)
        
        if not xml_trees:
            print(f"No TWB files found in {args.input_dir}")
            return 1
            
        print(f"Found {len(xml_trees)} TWB files")
        
        print("Finding common structure...")
        common_root = find_common_structure(xml_trees)
        
        # Save common structure
        common_file = os.path.join(args.output_dir, "common-twb.xml")
        save_xml_tree(common_root, common_file)
        print(f"Saved common structure to {common_file}")
        
        # Generate and save diff files
        print("Generating diff files...")
        for i, tree in enumerate(xml_trees):
            original_root = tree.getroot()
            
            # Generate diff
            diff_root = generate_xml_diff(original_root, common_root)
            
            # Construct filename from original file
            original_files = [f for f in os.listdir(args.input_dir) if f.lower().endswith('.twb')]
            if i < len(original_files):
                original_filename = original_files[i]
                base_name = os.path.splitext(original_filename)[0]
                diff_filename = f"{base_name}-diff.xml"
                
                # Save diff
                diff_path = os.path.join(args.output_dir, diff_filename)
                save_xml_tree(diff_root, diff_path)
                print(f"Generated diff for {original_filename}")
        
        print(f"All results saved to {args.output_dir}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 