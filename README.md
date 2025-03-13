# TWBCompare

A command-line tool for analyzing, comparing, and visualizing Tableau workbook (.twb) files.

## Features

TWBCompare helps you:

1. Convert multiple Tableau .twb files (XML format) to JSON for easier analysis
2. Find common tags, attributes, and hierarchies across multiple .twb files
3. Generate diffs to see what's unique in each .twb file compared to the common structure

## Installation

Since this tool is set up in a virtual environment, you can install it in development mode:

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

1. JSON versions of each .twb file in the output directory
2. A `common-twb.json` file with common elements across all files
3. Diff files for each .twb file showing what's unique compared to the common elements

## Requirements

- Python 3.6+

## License

MIT 