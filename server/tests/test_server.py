from __future__ import annotations

import asyncio
import json
import os
import unittest
from unittest.mock import patch

from server.main import (
    _is_sensitive_name,
    _mcp_transport_security,
    _valid_repo,
    _valid_repo_path,
    _validate_public_api_target,
    analyze_text_file,
    draft_automation_plan,
    web_search,
    mcp,
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

    def test_transport_security_uses_render_external_hostname(self):
        from mcp.server.transport_security import TransportSecuritySettings
        with patch.dict(os.environ, {"DEVNA_PUBLIC_HOST": "", "RENDER_EXTERNAL_HOSTNAME": "devna-example.onrender.com"}, clear=True):
            settings = _mcp_transport_security()
        self.assertIsInstance(settings, TransportSecuritySettings)
        self.assertEqual(settings.allowed_hosts, ["devna-example.onrender.com", "devna-example.onrender.com:*"])

    def test_transport_security_rejects_bad_hostname(self):
        with patch.dict(os.environ, {"DEVNA_PUBLIC_HOST": "https://evil.example/mcp", "RENDER_EXTERNAL_HOSTNAME": ""}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "hostname"):
                _mcp_transport_security()

    def test_sensitive_names_are_blocked(self):
        for name in (".env", ".env.production", "id_rsa", "private.key", "secrets.yaml", "credentials.json"):
            with self.subTest(name=name):
                self.assertTrue(_is_sensitive_name(name))
        self.assertFalse(_is_sensitive_name("main.py"))


class PublicMCPToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_server_exposes_expected_tool_names(self):
        from mcp import Client
        async with Client(mcp) as client:
            listed = await client.list_tools()
        names = {tool.name for tool in listed.tools}
        self.assertEqual(names, {
            "web_search",
            "github_get_repository",
            "github_list_issues",
            "github_read_file",
            "analyze_text_file",
            "fetch_allowlisted_api_json",
            "draft_automation_plan",
        })

    async def test_analyze_json_without_echoing_input(self):
        content = '{"ok": true}\n'
        result = json.loads(await analyze_text_file("config.json", content))
        self.assertTrue(result["json_valid"])
        self.assertEqual(result["line_count"], 1)
        self.assertFalse(result["content_echoed"])
        self.assertNotIn(content, json.dumps(result))

    async def test_analyze_csv_returns_aggregate_summary_without_echoing_cells(self):
        content = "name,city\\nAlice,Hyderabad\\nBob,Delhi\\n,Alice\\n"
        result = json.loads(await analyze_text_file("users.csv", content))
        self.assertTrue(result["tabular_valid"])
        self.assertEqual(result["header_column_count"], 2)
        self.assertEqual(result["data_row_count"], 3)
        self.assertEqual(result["column_summary"][0]["empty_cells"], 1)
        self.assertEqual(result["column_summary"][0]["distinct_values"], 2)
        self.assertNotIn("Alice", json.dumps(result))
        self.assertNotIn("Hyderabad", json.dumps(result))

    async def test_analyze_tsv_uses_tab_delimiter(self):
        content = "name\\tcity\\nAlice\\tHyderabad\\n"
        result = json.loads(await analyze_text_file("users.tsv", content))
        self.assertTrue(result["tabular_valid"])
        self.assertEqual(result["header_column_count"], 2)
        self.assertEqual(result["data_row_count"], 1)

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

    async def test_publisher_domain_challenge_requires_configured_token(self):
        from starlette.requests import Request
        from server.main import openai_domain_challenge
        scope = {"type": "http", "method": "GET", "path": "/.well-known/openai-apps-challenge", "headers": [], "query_string": b"", "server": ("testserver", 443), "client": ("127.0.0.1", 1234), "scheme": "https", "root_path": ""}
        request = Request(scope)
        with patch.dict(os.environ, {"OPENAI_APPS_CHALLENGE": ""}):
            response = await openai_domain_challenge(request)
            self.assertEqual(response.status_code, 404)
        with patch.dict(os.environ, {"OPENAI_APPS_CHALLENGE": "portal-verification-token"}):
            response = await openai_domain_challenge(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.body.decode("utf-8"), "portal-verification-token")

    async def test_public_web_search_returns_only_safe_source_links(self):
        class FakeDDGS:
            def __init__(self, timeout):
                self.timeout = timeout
            def text(self, query, **kwargs):
                return [
                    {"title": "Official Python docs", "href": "https://docs.python.org/3/library/asyncio.html", "body": "Task and timeout docs"},
                    {"title": "Bad scheme", "href": "javascript:alert(1)", "body": "unsafe"},
                    {"title": "Credential URL", "href": "https://user:pass@example.org/page", "body": "unsafe"},
                    {"title": "No host", "href": "https:///missing.example", "body": "unsafe"},
                ]
        with patch("server.main.DDGS", FakeDDGS):
            result = json.loads(await web_search("asyncio timeouts", max_results=3))
        self.assertEqual(result["result_count"], 1)
        self.assertEqual(result["results"][0]["url"], "https://docs.python.org/3/library/asyncio.html")
        self.assertIn("verify", result["note"].lower())

    async def test_github_read_file_refuses_sensitive_paths_before_network(self):
        from server.main import github_read_file
        with self.assertRaisesRegex(ValueError, "secret"):
            await github_read_file("octocat", "Hello-World", "config/.env.production")
        with self.assertRaisesRegex(ValueError, "private keys"):
            await github_read_file("octocat", "Hello-World", "private.pem")

    async def test_github_repository_tool_uses_public_data_fields(self):
        from unittest.mock import AsyncMock
        from server.main import github_get_repository
        payload = {"full_name": "octocat/Hello-World", "default_branch": "main", "private": False, "secret": "must not be returned"}
        with patch("server.main._get_json", new=AsyncMock(return_value=payload)):
            result = json.loads(await github_get_repository("octocat", "Hello-World"))
        self.assertEqual(result["full_name"], "octocat/Hello-World")
        self.assertEqual(result["default_branch"], "main")
        self.assertNotIn("secret", result)

    async def test_allowlisted_api_tool_is_read_only_and_returns_data(self):
        from unittest.mock import AsyncMock
        from server.main import fetch_allowlisted_api_json
        payload = {"rates": {"USD": 1.0}}
        with patch("server.main._get_json", new=AsyncMock(return_value=payload)) as mocked:
            result = json.loads(await fetch_allowlisted_api_json("api.frankfurter.app", "/latest?from=USD"))
        self.assertEqual(result["data"], payload)
        mocked.assert_awaited_once()
        self.assertEqual(mocked.await_args.args[0], "https://api.frankfurter.app/latest?from=USD")

    async def test_web_search_validates_arguments_before_network(self):
        with self.assertRaises(ValueError):
            await web_search("")
        with self.assertRaises(ValueError):
            await web_search("test", max_results=99)
        with self.assertRaises(ValueError):
            await web_search("test", region="not a region")


if __name__ == "__main__":
    unittest.main()
