#!/usr/bin/env python3
"""Unit tests for client module."""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected URL from payload."""
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        with patch('client.GithubOrgClient.org',
                   new_callable=lambda: property(lambda self: known_payload)):
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected list of repos."""
        test_payload = [
            {"name": "google/episodes.dart"},
            {"name": "google/cpp-netlib"},
            {"name": "google/dagger"}
        ]
        mock_get_json.return_value = test_payload

        test_url = "https://api.github.com/orgs/google/repos"
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=lambda: property(lambda self: test_url)):
            client = GithubOrgClient("test")
            result = client.public_repos()

            expected_repos = ["google/episodes.dart", "google/cpp-netlib",
                              "google/dagger"]
            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()
