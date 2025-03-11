"""
Unit tests for the parser module.
"""
import os
import unittest
from io import StringIO
from lxml import etree

from twbcompare.models import TagNode, FileStructure
from twbcompare.parser import parse_twb, _build_tag_node


class TestParser(unittest.TestCase):
    """Test cases for the parser module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary .twb file content
        self.test_xml = """<?xml version='1.0' encoding='utf-8' ?>
<workbook version="10.4">
  <preferences>
    <preference name="ui.encoding.shelf.height" value="24" />
    <preference name="ui.shelf.height" value="26" />
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
        
        # Create a test file
        self.test_file = "test_workbook.twb"
        with open(self.test_file, "w") as f:
            f.write(self.test_xml)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_build_tag_node(self):
        """Test _build_tag_node function."""
        # Parse XML string
        root = etree.parse(StringIO(self.test_xml)).getroot()
        
        # Build TagNode
        node = _build_tag_node(root)
        
        # Check node properties
        self.assertEqual(node.tag_name, "workbook")
        self.assertEqual(node.path, "/workbook")
        self.assertEqual(node.attributes, {"version": "10.4"})
        self.assertEqual(len(node.children), 3)  # preferences, datasources, worksheets
        
        # Check first child
        preferences = node.children[0]
        self.assertEqual(preferences.tag_name, "preferences")
        self.assertEqual(preferences.path, "/workbook/preferences")
        self.assertEqual(len(preferences.children), 2)  # two preference tags
    
    def test_parse_twb(self):
        """Test parse_twb function."""
        # Parse the test file
        structure = parse_twb(self.test_file)
        
        # Check structure properties
        self.assertIsNotNone(structure)
        self.assertEqual(structure.filename, "test_workbook.twb")
        
        # Check paths
        expected_paths = {
            "/workbook",
            "/workbook/preferences",
            "/workbook/preferences/preference",
            "/workbook/datasources",
            "/workbook/datasources/datasource",
            "/workbook/datasources/datasource/connection",
            "/workbook/worksheets",
            "/workbook/worksheets/worksheet",
            "/workbook/worksheets/worksheet/table"
        }
        self.assertTrue(expected_paths.issubset(structure.all_paths))
        
        # Check tags
        self.assertIn("workbook", structure.all_tags)
        self.assertIn("worksheet", structure.all_tags)
        self.assertIn("datasource", structure.all_tags)
        
        # Check attributes
        workbook_attrs = structure.all_tags["workbook"][0]
        self.assertEqual(workbook_attrs, {"version": "10.4"})
        
        worksheet_attrs = structure.all_tags["worksheet"][0]
        self.assertEqual(worksheet_attrs, {"name": "Sheet1"})


if __name__ == "__main__":
    unittest.main() 