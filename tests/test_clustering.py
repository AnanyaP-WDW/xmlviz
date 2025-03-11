"""
Unit tests for the clustering module.
"""
import os
import unittest
import tempfile
import shutil
from io import StringIO
from lxml import etree
import numpy as np

from twbcompare.models import TagNode, FileStructure, CommonStructure
from twbcompare.parser import _build_tag_node
from twbcompare.clustering import XMLClusterAnalyzer, cluster_xml_files


class TestClustering(unittest.TestCase):
    """Test cases for the clustering module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test XML content for multiple files
        self.xml_templates = [
            # File 1: Simple structure
            """<?xml version='1.0' encoding='utf-8' ?>
            <workbook version="10.4">
              <preferences>
                <preference name="ui.encoding.shelf.height" value="24" />
              </preferences>
              <worksheets>
                <worksheet name="Sheet1">
                  <table />
                </worksheet>
              </worksheets>
            </workbook>
            """,
            # File 2: Similar to File 1 with an extra worksheet
            """<?xml version='1.0' encoding='utf-8' ?>
            <workbook version="10.4">
              <preferences>
                <preference name="ui.encoding.shelf.height" value="24" />
              </preferences>
              <worksheets>
                <worksheet name="Sheet1">
                  <table />
                </worksheet>
                <worksheet name="Sheet2">
                  <table />
                </worksheet>
              </worksheets>
            </workbook>
            """,
            # File 3: Different structure with datasources
            """<?xml version='1.0' encoding='utf-8' ?>
            <workbook version="10.4">
              <preferences>
                <preference name="ui.encoding.shelf.height" value="24" />
              </preferences>
              <datasources>
                <datasource name="Sample">
                  <connection class="excel" />
                </datasource>
              </datasources>
              <worksheets>
                <worksheet name="Sheet1">
                  <table />
                </worksheet>
              </worksheets>
            </workbook>
            """
        ]
        
        # Parse XML and create FileStructure objects
        self.structures = []
        for i, xml in enumerate(self.xml_templates):
            root = etree.parse(StringIO(xml)).getroot()
            node = _build_tag_node(root)
            structure = FileStructure(f"test{i+1}.twb", node)
            self.structures.append(structure)
        
        # Create temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_xml_cluster_analyzer_init(self):
        """Test XMLClusterAnalyzer initialization."""
        analyzer = XMLClusterAnalyzer(self.structures)
        self.assertEqual(len(analyzer.structures), 3)
        self.assertIsNone(analyzer.feature_matrix)
        self.assertIsNone(analyzer.feature_names)
        self.assertIsNone(analyzer.clusters)
        self.assertIsNone(analyzer.n_clusters)
        self.assertIsNone(analyzer.model)
    
    def test_extract_features(self):
        """Test feature extraction."""
        analyzer = XMLClusterAnalyzer(self.structures)
        features = analyzer.extract_features()
        
        # Check matrix shape
        self.assertEqual(features.shape[0], 3)  # 3 files
        self.assertGreater(features.shape[1], 0)  # At least one feature
        
        # Check feature names
        self.assertIsNotNone(analyzer.feature_names)
        self.assertEqual(len(analyzer.feature_names), features.shape[1])
        
        # Check that some specific paths are included
        paths = analyzer.feature_names
        self.assertIn('/workbook', paths)
        self.assertIn('/workbook/worksheets', paths)
        self.assertIn('/workbook/worksheets/worksheet', paths)
    
    def test_compute_depth_features(self):
        """Test depth feature computation."""
        analyzer = XMLClusterAnalyzer(self.structures)
        depth_features = analyzer.compute_depth_features()
        
        # Check matrix shape
        self.assertEqual(depth_features.shape[0], 3)  # 3 files
        self.assertGreater(depth_features.shape[1], 0)  # At least one depth level
        
        # Check normalization (each row should sum to approximately 1)
        for i in range(depth_features.shape[0]):
            self.assertAlmostEqual(np.sum(depth_features[i]), 1.0, places=5)
    
    def test_kmeans_clustering(self):
        """Test K-means clustering."""
        analyzer = XMLClusterAnalyzer(self.structures)
        analyzer.extract_features()
        clusters = analyzer.cluster(n_clusters=2, method='kmeans')
        
        # Check clusters
        self.assertEqual(len(clusters), 2)  # 2 clusters
        self.assertEqual(len(analyzer.clusters), 2)
        self.assertEqual(analyzer.n_clusters, 2)
        
        # Check that all files are assigned to clusters
        total_files = sum(len(files) for files in clusters.values())
        self.assertEqual(total_files, 3)
    
    def test_hierarchical_clustering(self):
        """Test hierarchical clustering."""
        analyzer = XMLClusterAnalyzer(self.structures)
        analyzer.extract_features()
        clusters = analyzer.cluster(n_clusters=2, method='hierarchical')
        
        # Check clusters
        self.assertEqual(len(clusters), 2)  # 2 clusters
        self.assertEqual(len(analyzer.clusters), 2)
        self.assertEqual(analyzer.n_clusters, 2)
        
        # Check that all files are assigned to clusters
        total_files = sum(len(files) for files in clusters.values())
        self.assertEqual(total_files, 3)
    
    def test_find_cluster_commonalities(self):
        """Test finding commonalities within clusters."""
        analyzer = XMLClusterAnalyzer(self.structures)
        analyzer.extract_features()
        analyzer.cluster(n_clusters=2)
        
        # Find commonalities
        commonalities = analyzer.find_cluster_commonalities()
        
        # Check that we have commonalities for each cluster
        self.assertEqual(len(commonalities), 2)
        
        # Check that each cluster has some common paths
        for cluster_id, common in commonalities.items():
            self.assertGreater(len(common.common_paths), 0)
    
    def test_cluster_xml_files(self):
        """Test the cluster_xml_files function."""
        clusters, visualizations = cluster_xml_files(
            self.structures,
            n_clusters=2,
            method='kmeans',
            output_dir=self.temp_dir,
            output_format="png"
        )
        
        # Check clusters
        self.assertEqual(len(clusters), 2)
        
        # Check visualizations
        self.assertIn('clusters', visualizations)
        self.assertTrue(os.path.exists(visualizations['clusters']))
        self.assertIn('comparison_comparison', visualizations)
        self.assertTrue(os.path.exists(visualizations['comparison_comparison']))
        self.assertIn('comparison_depth', visualizations)
        self.assertTrue(os.path.exists(visualizations['comparison_depth']))


if __name__ == "__main__":
    unittest.main() 