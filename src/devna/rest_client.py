"""Configurable JSON REST client for a user-selected HTTPS API.

The base URL and optional bearer token are supplied locally through environment
variables. Write methods require a separate explicit confirmation flag.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_RESPONSE_BYTES = 2_000_000
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _validated_base_url(value: str | None) -> str:
    base = (value or os.environ.get("DEVNA_API_BASE_URL") or "").strip().rstrip("/")
    if not base:
        raise ValueError("Set DEVNA_API_BASE_URL to the trusted API base URL.")
    parsed = urlsplit(base)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("API base URL must be a clean HTTPS URL without credentials, query, or fragment.")
    return base


def request_json(
    path: str,
    *,
    method: str = "GET",
    payload: Any = None,
    confirmed: bool = False,
    base_url: str | None = None,
    token: str | None = None,
    timeout: int = 10,
) -> Any:
    """Call a path under a configured HTTPS base URL and parse a JSON response."""
    method = method.upper()
    if method not in ALLOWED_METHODS:
        raise ValueError(f"Method must be one of: {', '.join(sorted(ALLOWED_METHODS))}.")
    if not path.startswith("/") or path.startswith("//") or ".." in path.split("/"):
        raise ValueError("API path must be a local absolute path under the configured base URL.")
    if timeout < 1 or timeout > 60:
        raise ValueError("Timeout must be between 1 and 60 seconds.")
    is_write = method != "GET"
    if is_write and not confirmed:
        raise ValueError("API write requests require explicit confirmation.")
    base = _validated_base_url(base_url)
    auth_token = token or os.environ.get("DEVNA_API_TOKEN")
    if is_write and not (auth_token and auth_token.strip()):
        raise ValueError("Set DEVNA_API_TOKEN with the required API write permission.")

    headers = {
        "Accept": "application/json",
        "User-Agent": "DevNa-Core/0.1.0",
    }
    if auth_token and auth_token.strip():
        headers["Authorization"] = f"Bearer {auth_token.strip()}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{base}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise RuntimeError("API response exceeded the size limit.")
    except HTTPError as exc:
        safe_message = {
            401: "API rejected the credentials.",
            403: "API denied the request. Check permissions.",
            404: "API endpoint not found or not accessible.",
            429: "API rate limit reached. Wait before retrying.",
        }.get(exc.code, f"API request failed with HTTP {exc.code}.")
        raise RuntimeError(safe_message) from None
    except URLError:
        raise RuntimeError("Could not connect to the configured API. Check the network and base URL.") from None
    except TimeoutError:
        raise RuntimeError("API request timed out. Try again later.") from None

    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("The configured API returned a non-JSON response.") from None
