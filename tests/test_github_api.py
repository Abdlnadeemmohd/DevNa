from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from devna.github_api import (
    GitHubAPIError,
    _request,
    create_issue,
    get_repository,
    list_issues,
    parse_repository_slug,
)


class FakeResponse:
    def __init__(self, payload, headers=None):
        self.payload = json.dumps(payload).encode("utf-8")
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self.payload


class GitHubAPITests(unittest.TestCase):
    def test_repository_slug_validation(self):
        self.assertEqual(parse_repository_slug("owner/repo"), ("owner", "repo"))
        self.assertEqual(parse_repository_slug("owner/repo.git"), ("owner", "repo"))
        for bad_value in ("", "owner", "owner/repo/extra", "../repo", "owner/../repo"):
            with self.subTest(value=bad_value):
                with self.assertRaises(ValueError):
                    parse_repository_slug(bad_value)

    @patch("devna.github_api.urlopen")
    def test_get_repository_uses_fixed_api_host(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({
            "full_name": "octocat/hello-world",
            "html_url": "https://github.com/octocat/hello-world",
            "private": False,
            "default_branch": "main",
            "stargazers_count": 3,
        })
        result = get_repository("octocat/hello-world")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.github.com/repos/octocat/hello-world")
        self.assertEqual(result["full_name"], "octocat/hello-world")
        self.assertFalse(result["private"])

    @patch("devna.github_api.urlopen")
    def test_token_is_sent_as_authorization_header(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"full_name": "octocat/hello-world"})
        get_repository("octocat/hello-world", token="test-token")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    @patch("devna.github_api.urlopen")
    def test_issues_filters_pull_requests(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse([
            {"number": 1, "title": "Bug", "state": "open", "labels": []},
            {"number": 2, "title": "Change", "state": "open", "pull_request": {"url": "https://api.github.com/pr/2"}, "labels": []},
        ])
        issues = list_issues("octocat/hello-world")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["number"], 1)

    def test_issue_creation_requires_explicit_confirmation(self):
        with patch("devna.github_api.urlopen") as mock_urlopen:
            with self.assertRaisesRegex(ValueError, "explicit confirmation"):
                create_issue("octocat/hello-world", title="Test", confirmed=False, token="token")
            mock_urlopen.assert_not_called()

    def test_issue_creation_requires_token(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "", "GH_TOKEN": ""}):
            with self.assertRaisesRegex(GitHubAPIError, "Set GITHUB_TOKEN or GH_TOKEN"):
                create_issue("octocat/hello-world", title="Test", confirmed=True, token=None)

    @patch("devna.github_api.urlopen")
    def test_create_issue_posts_only_expected_fields(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({
            "number": 7,
            "title": "A test issue",
            "html_url": "https://github.com/octocat/hello-world/issues/7",
            "state": "open",
        })
        result = create_issue(
            "octocat/hello-world",
            title=" A test issue ",
            body="Details",
            confirmed=True,
            token="test-token",
        )
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"title": "A test issue", "body": "Details"})
        self.assertEqual(result["number"], 7)

    def test_endpoint_cannot_escape_fixed_api_host(self):
        with self.assertRaises(ValueError):
            _request("//evil.example/path")
        with self.assertRaises(ValueError):
            _request("/repos/../secrets")


if __name__ == "__main__":
    unittest.main()
