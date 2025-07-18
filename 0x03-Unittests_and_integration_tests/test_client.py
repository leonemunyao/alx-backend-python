#!/usr/bin/env python3
"""Tests cases for the client module"""

import unittest
from parameterized import parameterized
from client import GithubOrgClient
from unittest.mock import patch, Mock, PropertyMock


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

    def test_public_repos_url(self):
        """Test that GithubOrgClient.public_repos_url returns
        the correct value."""

        mock_org_payload = {
            "login": "google",
            "id": 12345,
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Use patch as a context manager to mock the org property
        with patch.object(GithubOrgClient, 'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = mock_org_payload

            client = GithubOrgClient("google")
            result = client.public_repos_url

            # Verify that the repos_url is correctly returned
            self.assertEqual(result, mock_org_payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that GithubOrgClient.public_repos returns
        the expected list of repos."""

        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]

        mock_repos_url = "https://api.github.com/orgs/google/repos"

        mock_get_json.return_value = mock_repos_payload

        # Use context manager to mock the public_repos_url property
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = mock_repos_url

            client = GithubOrgClient("google")
            result = client.public_repos()

            # Verify that the result matches the expected list of repos
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            mock_public_repos_url.assert_called_once()

        # Verify get_json was called with mocked URL
        mock_get_json.assert_called_once_with(mock_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", expected=True),
        ({"license": {"key": "other_license"}}, "my_license", expected=False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that GithubOrgClient.has_license returns the correct value."""
        client = GithubOrgClient("google")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)
