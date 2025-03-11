# TwbCompare

A tool for analyzing, comparing, and visualizing Tableau .twb files. It helps identify structural similarities between workbooks and creates cluster visualizations.

## Features

- Analyzes multiple Tableau workbook (.twb) files
- Identifies common structures and patterns
- Creates interactive cluster visualizations
- Generates common TWB files for all files and each cluster
- Provides detailed reports of commonalities

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install the required packages:
```bash
pip install pandas plotly numpy matplotlib scikit-learn
pip install -e .
```

## Usage

Basic usage:
```bash
source venv/bin/activate && twbcompare /path/to/twb/files --output-dir output_directory
```

Example:
```bash
source venv/bin/activate && twbcompare /Users/username/Desktop/twb_files --output-dir twbcompare_results
```

### Options

- `--output-dir`: Directory for output files (default: twbcompare_output)
- `--n-clusters`: Number of clusters to create (default: 3)
- `--threshold`: Minimum frequency threshold for commonality (0.0-1.0, default: 1.0)
- `--placeholders`: Use placeholder values in generated TWB files
- `--verbose`: Enable detailed logging

### Output Files

The tool generates the following outputs:

1. Common TWB file for all input files:
   - `output_directory/common.twb`

2. Interactive cluster visualization:
   - `output_directory/clusters/clusters.html`

3. For each cluster X:
   - `output_directory/clusters/cluster_X/cluster_X_common.twb` - Common TWB file
   - `output_directory/clusters/cluster_X/report.txt` - Cluster report

4. Comparison visualizations:
   - `output_directory/clusters/comparisons/cluster_comparison.png`
   - `output_directory/clusters/comparisons/depth_distribution.png`

## License

[MIT License](LICENSE) 