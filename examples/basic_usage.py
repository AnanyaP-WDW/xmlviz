#!/usr/bin/env python3
"""
Basic usage example for the TwbCompare library.

This script demonstrates how to:
1. Parse a directory of .twb files
2. Analyze commonalities
3. Generate visualizations
4. Create a mock .twb file
5. Generate a report
"""
import os
import sys
from twbcompare.parser import parse_directory
from twbcompare.analyzer import find_commonalities, get_stats_report
from twbcompare.visualizer import visualize_commonalities
from twbcompare.generator import generate_mock_twb_with_placeholders


def main():
    """Run the basic usage example."""
    # Check for input directory argument
    if len(sys.argv) < 2:
        print("Usage: python basic_usage.py /path/to/twb/files")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    print(f"Analyzing .twb files in {input_dir}")
    
    # Create output directory
    output_dir = "example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Parse .twb files
    structures = parse_directory(input_dir)
    if not structures:
        print("No valid .twb files found.")
        sys.exit(1)
    
    print(f"Parsed {len(structures)} .twb files successfully")
    
    # 2. Analyze commonalities with a 90% threshold
    common = find_commonalities(structures, threshold=0.9)
    print(f"Found {len(common.common_paths)} common paths and {len(common.common_tags)} common tags")
    
    # 3. Generate visualization
    viz_file = os.path.join(output_dir, "common_structure")
    visualize_commonalities(common, viz_file)
    print(f"Visualization saved to {viz_file}.png")
    
    # 4. Generate mock .twb file with placeholders
    mock_file = os.path.join(output_dir, "common.twb")
    generate_mock_twb_with_placeholders(common, mock_file)
    print(f"Mock .twb file saved to {mock_file}")
    
    # 5. Generate a report
    report = get_stats_report(common, len(structures))
    report_file = os.path.join(output_dir, "report.txt")
    with open(report_file, "w") as f:
        f.write(report)
    print(f"Report saved to {report_file}")
    
    print("\nExample completed. Check the 'example_output' directory for results.")


if __name__ == "__main__":
    main() 