"""
Command-line interface for the TWBCompare tool.
"""
import os
import sys
import argparse
from typing import List, Optional

from twbcompare.utils.xml_analyzer import find_common_twb_structure

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
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="Proportion (0.0-1.0) of files that must contain an element for it to be considered common"
    )
    
    parsed_args = parser.parse_args(args)
    input_dir = parsed_args.input_dir
    output_dir = parsed_args.output_dir
    threshold = parsed_args.threshold
    
    # Validate threshold
    if threshold < 0.0 or threshold > 1.0:
        print("Error: Threshold must be between 0.0 and 1.0")
        return 1
    
    try:
        # Check if input directory exists
        if not os.path.isdir(input_dir):
            print(f"Error: Input directory '{input_dir}' does not exist or is not a directory")
            return 1
        
        # Process all TWB files directly as XML
        print(f"Processing .twb files from '{input_dir}'...")
        print(f"Using threshold: {threshold} ({int(threshold*100)}%)")
        
        # Find common structure and generate diffs
        common_file, diff_files = find_common_twb_structure(input_dir, output_dir, threshold)
        
        if not diff_files:
            print(f"No .twb files found in '{input_dir}'")
            return 1
        
        print(f"Saved common structure to '{common_file}'")
        print(f"Generated {len(diff_files)} diff files")
        
        print(f"\nAll results saved to '{output_dir}'")
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 