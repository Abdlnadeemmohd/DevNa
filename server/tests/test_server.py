from __future__ import annotations

import asyncio
import json
import os
import unittest
from unittest.mock import patch

from server.main import (
    _is_sensitive_name,
    _valid_repo,
    _valid_repo_path,
    _validate_public_api_target,
    analyze_text_file,
    draft_automation_plan,
    web_search,
)


class PublicMCPValidationTests(unittest.TestCase):
    def test_repository_identifiers_are_validated(self):
        self.assertEqual(_valid_repo("octocat", "Hello-World"), ("octocat", "Hello-World"))
        for owner, repo in (("../x", "repo"), ("owner", "../repo"), ("", "repo"), ("owner", "x/y")):
            with self.subTest(owner=owner, repo=repo):
                with self.assertRaises(ValueError):
                    _valid_repo(owner, repo)

    def test_repository_paths_cannot_escape_root(self):
        self.assertEqual(_valid_repo_path("src/main.py"), "src/main.py")
        for path in ("", "/etc/passwd", "../README.md", "src/../secret", r"src\main.py"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    _valid_repo_path(path)

    def test_api_hosts_must_be_allowlisted_and_path_is_relative(self):
        self.assertEqual(
            _validate_public_api_target("API.GITHUB.COM", "/repos/octocat/Hello-World"),
            ("api.github.com", "/repos/octocat/Hello-World"),
        )
        with self.assertRaisesRegex(ValueError, "not allowlisted"):
            _validate_public_api_target("example.com", "/")
        for path in ("//evil.example", "https://evil.example/path", "/../secret", "/v1/items#frag"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    _validate_public_api_target("api.github.com", path)

    def test_api_allowlist_can_be_extended_by_deployment_owner(self):
        with patch.dict(os.environ, {"DEVNA_ALLOWED_API_HOSTS": "api.example.test,api2.example.test"}):
            self.assertEqual(
                _validate_public_api_target("api.example.test", "/v1/status"),
                ("api.example.test", "/v1/status"),
            )

    def test_sensitive_names_are_blocked(self):
        for name in (".env", ".env.production", "id_rsa", "private.key", "secrets.yaml", "credentials.json"):
            with self.subTest(name=name):
                self.assertTrue(_is_sensitive_name(name))
        self.assertFalse(_is_sensitive_name("main.py"))


class PublicMCPToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_analyze_json_without_echoing_input(self):
        content = '{"ok": true}\n'
        result = json.loads(await analyze_text_file("config.json", content))
        self.assertTrue(result["json_valid"])
        self.assertEqual(result["line_count"], 1)
        self.assertFalse(result["content_echoed"])
        self.assertNotIn(content, json.dumps(result))

    async def test_analyze_invalid_python_without_execution(self):
        content = "def broken(:\n    print('not run')"
        result = json.loads(await analyze_text_file("example.py", content))
        self.assertEqual(result["python_syntax"], "invalid")
        self.assertFalse(result["content_echoed"])
        self.assertNotIn("not run", json.dumps(result))

    async def test_secret_filename_is_refused(self):
        with self.assertRaisesRegex(ValueError, "refuses to analyze"):
            await analyze_text_file(".env.production", "TOKEN=never-print")

    async def test_input_size_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "150,000"):
            await analyze_text_file("large.txt", "x" * 150_001)

    async def test_automation_plan_never_executes(self):
        result = json.loads(await draft_automation_plan("Delete a production database"))
        self.assertFalse(result["execution_performed"])
        self.assertTrue(result["approval_required_before_consequential_action"])
        self.assertTrue(any("approval" in step.lower() or "approval" in result["steps"][4].lower() for step in result["steps"]))

    async def test_web_search_validates_arguments_before_network(self):
        with self.assertRaises(ValueError):
            await web_search("")
        with self.assertRaises(ValueError):
            await web_search("test", max_results=99)
        with self.assertRaises(ValueError):
            await web_search("test", region="not a region")


if __name__ == "__main__":
    unittest.main()
