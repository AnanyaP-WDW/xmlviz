"""
Unit tests for the analyzer module.
"""
import unittest
from io import StringIO
from lxml import etree

from twbcompare.models import TagNode, FileStructure, CommonStructure
from twbcompare.parser import _build_tag_node
from twbcompare.analyzer import find_commonalities, _find_common_paths, _find_common_tags_and_attributes


class TestAnalyzer(unittest.TestCase):
    """Test cases for the analyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test XML strings for two similar workbooks
        self.xml1 = """<?xml version='1.0' encoding='utf-8' ?>
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
        
        self.xml2 = """<?xml version='1.0' encoding='utf-8' ?>
<workbook version="10.5">
  <preferences>
    <preference name="ui.encoding.shelf.height" value="26" />
  </preferences>
  <worksheets>
    <worksheet name="Sheet2">
      <table />
    </worksheet>
    <worksheet name="Sheet3">
      <table />
    </worksheet>
  </worksheets>
</workbook>
"""
        
        # Create FileStructure objects
        root1 = etree.parse(StringIO(self.xml1)).getroot()
        node1 = _build_tag_node(root1)
        self.structure1 = FileStructure("file1.twb", node1)
        
        root2 = etree.parse(StringIO(self.xml2)).getroot()
        node2 = _build_tag_node(root2)
        self.structure2 = FileStructure("file2.twb", node2)
        
        self.structures = [self.structure1, self.structure2]
    
    def test_find_common_paths(self):
        """Test _find_common_paths function."""
        # Find common paths with threshold 1.0 (100%)
        common_paths, path_frequency = _find_common_paths(self.structures, 1.0)
        
        # Expected common paths (present in both files)
        expected_paths = {
            "/workbook",
            "/workbook/preferences",
            "/workbook/preferences/preference",
            "/workbook/worksheets",
            "/workbook/worksheets/worksheet",
            "/workbook/worksheets/worksheet/table"
        }
        
        self.assertEqual(common_paths, expected_paths)
        
        # Check frequency
        for path in expected_paths:
            self.assertEqual(path_frequency[path], 1.0)
        
        # Test with lower threshold
        common_paths_90, _ = _find_common_paths(self.structures, 0.5)
        self.assertGreaterEqual(len(common_paths_90), len(common_paths))
    
    def test_find_common_tags_and_attributes(self):
        """Test _find_common_tags_and_attributes function."""
        # Find common tags with threshold 1.0
        common_tags, tag_frequency = _find_common_tags_and_attributes(self.structures, 1.0)
        
        # Expected common tags
        expected_tags = {"workbook", "preferences", "preference", "worksheets", "worksheet", "table"}
        self.assertEqual(set(common_tags.keys()), expected_tags)
        
        # Check attribute commonality
        self.assertIn("name", common_tags["preference"][0])  # 'name' attribute is common
        self.assertIn("name", common_tags["worksheet"][0])   # 'name' attribute is common
        
        # Values should be empty since they differ
        self.assertEqual(common_tags["preference"][0]["name"], "")
        self.assertEqual(common_tags["worksheet"][0]["name"], "")
        
        # Check frequency
        for tag in expected_tags:
            self.assertEqual(tag_frequency[tag], 1.0)
    
    def test_find_commonalities(self):
        """Test find_commonalities function."""
        # Find commonalities
        common = find_commonalities(self.structures)
        
        # Check that it populated both paths and tags
        self.assertIsInstance(common, CommonStructure)
        self.assertTrue(len(common.common_paths) > 0)
        self.assertTrue(len(common.common_tags) > 0)
        
        # Check that frequency dictionaries were populated
        self.assertTrue(len(common.path_frequency) > 0)
        self.assertTrue(len(common.tag_frequency) > 0)
        
        # Test with no structures
        empty_common = find_commonalities([])
        self.assertEqual(len(empty_common.common_paths), 0)
        self.assertEqual(len(empty_common.common_tags), 0)


if __name__ == "__main__":
    unittest.main() 