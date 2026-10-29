from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from scripts.build_public_plugin import main as build_main, require_https, verify_endpoint


class PublicPackageBuilderTests(unittest.TestCase):
    def test_require_https_accepts_public_endpoint(self):
        self.assertEqual(
            require_https("https://devna.example.org/mcp", "MCP URL"),
            "https://devna.example.org/mcp",
        )

    def test_demo_url_accepts_standard_video_query_parameters(self):
        url = "https://youtu.be/AbCdEfG1234?feature=share"
        self.assertEqual(
            require_https(url, "Demo URL", allow_query_fragment=True),
            url,
        )

    def test_demo_url_still_rejects_embedded_credentials(self):
        with self.assertRaises(SystemExit):
            require_https(
                "https://user:password@video.example/watch?v=AbCdEfG1234",
                "Demo URL",
                allow_query_fragment=True,
            )

    def test_require_https_rejects_http_and_embedded_credentials(self):
        for url in (
            "http://devna.example.org/mcp",
            "https://user:password@devna.example.org/mcp",
            "https://devna.example.org/mcp?token=x",
            "https://devna.example.org/mcp#fragment",
        ):
            with self.subTest(url=url):
                with self.assertRaises(SystemExit):
                    require_https(url, "MCP URL")

    @patch("scripts.build_public_plugin.urllib.request.urlopen")
    def test_verify_endpoint_checks_health_route(self, mock_urlopen):
        class FakeResponse:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def read(self, _limit=4096):
                return json.dumps({"ok": True, "service": "DevNa"}).encode("utf-8")

        mock_urlopen.return_value = FakeResponse()
        verify_endpoint("https://devna.example.org/mcp")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://devna.example.org/healthz")

    @patch.dict("os.environ", {"DEVNA_MCP_URL": "", "DEVNA_DEMO_RECORDING_URL": ""})
    def test_build_fails_without_live_endpoint_and_demo(self):
        with self.assertRaisesRegex(SystemExit, "Set both DEVNA_MCP_URL and DEVNA_DEMO_RECORDING_URL"):
            build_main()


if __name__ == "__main__":
    unittest.main()
