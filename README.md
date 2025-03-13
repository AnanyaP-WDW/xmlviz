# TWBCompare

A command-line tool for analyzing and comparing Tableau workbook (.twb) files directly as XML.

## Features

TWBCompare helps you:

1. Analyze multiple Tableau .twb files directly in their native XML format
2. Find common XML elements, attributes, and hierarchies across multiple .twb files
3. Generate a common XML structure that represents elements present in all files
4. Generate diffs to see what's unique in each .twb file compared to the common structure

## Installation

You can install the package in development mode:

```bash
# Activate the virtual environment
source venv/bin/activate

# Install in development mode
pip install -e .
```

## Usage

The basic usage is:

```bash
twbcompare /path/to/twb/files --output-dir twbcompare_results
```

### Arguments

- `input_dir` (required): Directory containing .twb files to analyze
- `--output-dir` (optional): Directory to save results (default: "twbcompare_results")

### Example

```bash
twbcompare /Users/ananyapathak/Desktop/PBI --output-dir twbcompare_results
```

## Output

The tool generates:

1. A `common-twb.xml` file containing the common structure across all files
2. XML diff files for each .twb file showing what's unique compared to the common structure

## How It Works

TWBCompare uses a recursive algorithm to find the common structure across all TWB files:

1. It parses all TWB files as XML directly using ElementTree
2. Starting with the first file as a base, it iteratively compares with other files
3. For each comparison, it keeps only the elements and attributes that match across files
4. The algorithm handles nested structures by recursively comparing children
5. After finding the common structure, it generates diff files by comparing each original file with the common structure

## Requirements

- Python 3.6+
- lxml 4.6.0+

## License

MIT 