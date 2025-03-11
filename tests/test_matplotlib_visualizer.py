"""
Unit tests for the matplotlib_visualizer module.
"""
import os
import unittest
from io import StringIO
import tempfile
import shutil
from lxml import etree

from twbcompare.models import TagNode, FileStructure, CommonStructure
from twbcompare.parser import _build_tag_node
from twbcompare.matplotlib_visualizer import (
    visualize_structure,
    visualize_commonalities,
    visualize_file_structure
)


class TestMatplotlibVisualizer(unittest.TestCase):
    """Test cases for the matplotlib_visualizer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test XML content
        self.test_xml = """<?xml version='1.0' encoding='utf-8' ?>
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
"""
        # Parse the test XML to create a TagNode
        root = etree.parse(StringIO(self.test_xml)).getroot()
        self.root_node = _build_tag_node(root)
        
        # Create a FileStructure
        self.structure = FileStructure("test.twb", self.root_node)
        
        # Create temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_visualize_structure(self):
        """Test visualize_structure function."""
        # Create output file path
        output_file = os.path.join(self.temp_dir, "test_structure")
        
        # Test with PNG format
        output_path = visualize_structure(self.structure, output_file, output_format="png")
        
        # Check if the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".png"))
    
    def test_visualize_commonalities(self):
        """Test visualize_commonalities function."""
        # Create a CommonStructure with some test data
        common = CommonStructure()
        common.common_paths = self.structure.all_paths
        common.common_tags = self.structure.all_tags
        
        # Add frequency data
        common.path_frequency = {path: 1.0 for path in common.common_paths}
        common.tag_frequency = {tag: 1.0 for tag in common.common_tags}
        
        # Create output file path
        output_file = os.path.join(self.temp_dir, "test_common")
        
        # Test with PNG format
        output_path = visualize_commonalities(common, output_file, output_format="png")
        
        # Check if the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".png"))
    
    def test_visualize_file_structure(self):
        """Test visualize_file_structure function."""
        # Create a CommonStructure with some test data
        common = CommonStructure()
        common.common_paths = self.structure.all_paths
        common.common_tags = self.structure.all_tags
        
        # Add frequency data
        common.path_frequency = {path: 1.0 for path in common.common_paths}
        common.tag_frequency = {tag: 1.0 for tag in common.common_tags}
        
        # Test with PNG format
        output_path = visualize_file_structure(
            self.structure,
            common,
            self.temp_dir,
            output_format="png"
        )
        
        # Check if the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".png"))


if __name__ == "__main__":
    unittest.main() 