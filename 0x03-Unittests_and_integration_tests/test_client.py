#!/usr/bin/env python3
"""Tests cases for the client module"""

import unittest
from parameterized import parameterized
from client import GithubOrgClient
from unittest.mock import patch, Mock


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient. The org method should
    call get_json with a formatted URL."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""

        # Define what the mock should return
        expected_org_data = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_org_data

        # Create client with thee parameterized org_name
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Calculate what URL should have been called
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Verify that the mock was called with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Verify that the result matches the expected data
        self.assertEqual(result, expected_org_data)
