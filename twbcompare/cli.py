"""
Command-line interface for the TWBCompare tool.
"""
import os
import sys
import argparse
from typing import List, Optional

from twbcompare.utils.parser import convert_all_twb_files
from twbcompare.utils.analyzer import (
    find_common_elements,
    save_common_elements,
    save_diff_files
)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the TWBCompare CLI.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        description="TWBCompare - A tool for analyzing Tableau .twb files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_dir",
        help="Directory containing .twb files to analyze"
    )
    
    parser.add_argument(
        "--output-dir",
        default="twbcompare_results",
        help="Directory to save results"
    )
    
    parsed_args = parser.parse_args(args)
    input_dir = parsed_args.input_dir
    output_dir = parsed_args.output_dir
    
    try:
        # Check if input directory exists
        if not os.path.isdir(input_dir):
            print(f"Error: Input directory '{input_dir}' does not exist or is not a directory")
            return 1
        
        # Step 1: Convert all TWB files to JSON
        print(f"Converting .twb files from '{input_dir}' to JSON...")
        json_files = convert_all_twb_files(input_dir, output_dir)
        
        if not json_files:
            print(f"No .twb files found in '{input_dir}'")
            return 1
        
        print(f"Converted {len(json_files)} .twb files to JSON")
        
        # Step 2: Find common elements
        print("Finding common elements across all .twb files...")
        common_elements = find_common_elements(json_files)
        
        # Save common elements
        common_file = save_common_elements(common_elements, output_dir)
        print(f"Saved common elements to '{common_file}'")
        
        # Step 3: Generate diff files
        print("Generating diff files...")
        diff_files = save_diff_files(json_files, common_elements, output_dir)
        print(f"Generated {len(diff_files)} diff files")
        
        print(f"\nAll results saved to '{output_dir}'")
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 