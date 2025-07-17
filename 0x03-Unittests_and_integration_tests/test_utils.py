#!/usr/bin/env python3
"""Test cases for access_nested_map function."""

import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """This decorator takes a list of test cases and runs the
    test method for each case."""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test method to receive parameters from the decorator."""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)
