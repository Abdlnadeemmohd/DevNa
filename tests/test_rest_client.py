from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from devna.rest_client import request_json


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self.payload


class RestClientTests(unittest.TestCase):
    def test_requires_configured_https_base(self):
        with self.assertRaisesRegex(ValueError, "DEVNA_API_BASE_URL"):
            request_json("/items", base_url="")
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            request_json("/items", base_url="http://api.example.com")
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            request_json("/items", base_url="https://user:password@api.example.com")

    def test_rejects_paths_outside_configured_base(self):
        for path in ("items", "//evil.example/path", "/../secret"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    request_json(path, base_url="https://api.example.com")

    def test_get_does_not_accept_a_request_body(self):
        with self.assertRaisesRegex(ValueError, "GET requests must not include"):
            request_json(
                "/items", method="GET", payload={"x": 1},
                base_url="https://api.example.com",
            )

    def test_write_requires_explicit_confirmation_before_network(self):
        with patch("devna.rest_client.urlopen") as mock_urlopen:
            with self.assertRaisesRegex(ValueError, "explicit confirmation"):
                request_json("/items", method="POST", base_url="https://api.example.com", token="t")
            mock_urlopen.assert_not_called()

    def test_write_requires_token(self):
        with patch.dict(os.environ, {"DEVNA_API_TOKEN": ""}):
            with self.assertRaisesRegex(ValueError, "DEVNA_API_TOKEN"):
                request_json(
                    "/items", method="POST", confirmed=True,
                    base_url="https://api.example.com", token=None,
                )

    @patch("devna.rest_client.urlopen")
    def test_get_parses_json_and_uses_configured_base(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"items": [1, 2]})
        result = request_json("/v1/items", base_url="https://api.example.com")
        self.assertEqual(result, {"items": [1, 2]})
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.example.com/v1/items")
        self.assertEqual(request.method, "GET")

    @patch("devna.rest_client.urlopen")
    def test_confirmed_write_sends_json_and_bearer_token(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"created": True})
        result = request_json(
            "/v1/items",
            method="POST",
            payload={"name": "demo"},
            confirmed=True,
            base_url="https://api.example.com",
            token="secret-token",
        )
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"name": "demo"})
        self.assertTrue(result["created"])


if __name__ == "__main__":
    unittest.main()
