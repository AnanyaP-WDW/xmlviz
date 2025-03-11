# TwbCompare

A Python-based tool for analyzing, comparing, and visualizing Tableau .twb files.

## Overview

TwbCompare is a command-line tool that helps you analyze multiple Tableau workbook files (.twb) to understand their structure, identify common elements, visualize the hierarchy, and generate a mock .twb file based on common elements. It also includes clustering functionality to group similar .twb files based on their structure.

### Features

- **XML Parsing and Analysis**: Parse multiple .twb files to extract tags, attributes, and hierarchy.
- **Commonality Analysis**: Identify common elements across files (tags, attributes, paths).
- **Visualization**: Generate tree diagrams of .twb structures and common elements using Matplotlib and NetworkX.
- **Mock File Generation**: Create a skeletal .twb file based on common elements.
- **Reporting**: Generate detailed reports in text or JSON format.
- **Clustering**: Group similar .twb files based on their structure and analyze commonalities within clusters.

## Installation

### Requirements

- Python 3.9 or higher
- Required libraries: lxml, matplotlib, networkx, scikit-learn, pandas, scipy, numpy

### Install from PyPI

```bash
pip install twbcompare
```

### Install from Source

```bash
git clone https://github.com/twbcompare/twbcompare.git
cd twbcompare
pip install -e .
```

## Usage

### Basic Usage

```bash
twbcompare /path/to/twb/files
```

This will:
1. Parse all .twb files in the specified directory
2. Identify common elements
3. Generate visualizations
4. Create a mock .twb file
5. Generate a text report

### Clustering Usage

```bash
twbcompare /path/to/twb/files --cluster --n-clusters 3 --cluster-method kmeans
```

This will:
1. Parse all .twb files in the specified directory
2. Perform basic analysis as above
3. Cluster the files into 3 groups using K-means
4. Generate cluster visualizations
5. Analyze commonalities within each cluster

### Command-line Options

```
usage: twbcompare [-h] [-o OUTPUT_DIR] [-t THRESHOLD] [-f {png,svg}] [--no-viz] [--no-mock] [--placeholders] [--json] [--verbose] [--cluster] [--n-clusters N_CLUSTERS] [--cluster-method {kmeans,hierarchical}] input_dir

TwbCompare - Analyze and compare Tableau .twb files

positional arguments:
  input_dir             Directory containing .twb files to analyze

optional arguments:
  -h, --help            show this help message and exit
  -o, --output-dir      Directory for output files (default: twbcompare_output)
  -t, --threshold       Minimum frequency threshold for commonality (0.0-1.0) (default: 1.0)
  -f, --format          Output format for visualizations (png or svg) (default: png)
  --no-viz              Skip visualization generation
  --no-mock             Skip mock .twb file generation
  --placeholders        Use placeholder values for empty attributes in the mock .twb file
  --json                Output report in JSON format
  --verbose             Enable verbose logging
  --cluster             Perform clustering of .twb files
  --n-clusters          Number of clusters to create (default: 3)
  --cluster-method      Clustering method to use (kmeans or hierarchical) (default: kmeans)
```

### Examples

Analyze files with a 90% commonality threshold:
```bash
twbcompare /path/to/twb/files -t 0.9
```

Skip visualizations and generate JSON report:
```bash
twbcompare /path/to/twb/files --no-viz --json
```

Generate SVG visualizations and use placeholder values:
```bash
twbcompare /path/to/twb/files -f svg --placeholders
```

Cluster files using hierarchical clustering:
```bash
twbcompare /path/to/twb/files --cluster --cluster-method hierarchical
```

## Output

The tool generates the following outputs in the specified output directory (default: `twbcompare_output`):

- `report.txt` or `report.json`: Report of common elements and their frequency
- `visualizations/`: Directory containing visualization files:
  - `common_structure.png`: Visualization of common elements
  - Individual .twb file structure visualizations
- `common.twb`: Mock .twb file based on common elements
- `clusters/` (if clustering is enabled):
  - `clusters.png`: Visualization of file clusters
  - `dendrogram.png`: Hierarchical clustering dendrogram (if using hierarchical clustering)
  - `comparisons/`: Visualizations comparing clusters
  - `cluster_X/`: Directory for each cluster with its own analysis

## Library Usage

TwbCompare can also be used as a Python library:

### Basic Analysis

```python
from twbcompare.parser import parse_directory
from twbcompare.analyzer import find_commonalities
from twbcompare.matplotlib_visualizer import visualize_commonalities
from twbcompare.generator import generate_mock_twb

# Parse .twb files
structures = parse_directory("/path/to/twb/files")

# Find commonalities
common = find_commonalities(structures, threshold=0.9)

# Generate visualization
visualize_commonalities(common, "common_structure")

# Generate mock .twb file
generate_mock_twb(common, "common.twb")
```

### Clustering Analysis

```python
from twbcompare.parser import parse_directory
from twbcompare.clustering import XMLClusterAnalyzer

# Parse .twb files
structures = parse_directory("/path/to/twb/files")

# Initialize cluster analyzer
analyzer = XMLClusterAnalyzer(structures)

# Extract features and cluster
analyzer.extract_features()
clusters = analyzer.cluster(n_clusters=3, method="kmeans")

# Visualize clusters
analyzer.visualize_clusters("clusters")

# Find commonalities within each cluster
commonalities = analyzer.find_cluster_commonalities()

# Generate cluster comparisons
analyzer.visualize_cluster_comparisons(commonalities, "comparisons")
```

## License

MIT License 