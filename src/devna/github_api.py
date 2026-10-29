"""Small, dependency-free GitHub REST API client.

Reads public data without a token. Write operations require a token supplied through
GITHUB_TOKEN or GH_TOKEN and an explicit confirmation argument.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 2_000_000
_REPO_PART = re.compile(r"^[A-Za-z0-9_.-]+$")


class GitHubAPIError(RuntimeError):
    """A safe, user-facing error from the GitHub API client."""


def parse_repository_slug(value: str) -> tuple[str, str]:
    """Validate and split an OWNER/REPO string."""
    candidate = value.strip().removesuffix(".git")
    parts = candidate.split("/")
    if len(parts) != 2 or not all(_REPO_PART.fullmatch(part) for part in parts):
        raise ValueError("Repository must use OWNER/REPO format.")
    if parts[0] in {".", ".."} or parts[1] in {".", ".."}:
        raise ValueError("Repository owner and name are invalid.")
    return parts[0], parts[1]


def _token_from_environment() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return token.strip() if token and token.strip() else None


def _request(
    endpoint: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    """Make a bounded request to the fixed GitHub API host."""
    if not endpoint.startswith("/") or endpoint.startswith("//") or ".." in endpoint.split("/"):
        raise ValueError("Invalid GitHub API endpoint.")
    if timeout < 1 or timeout > 60:
        raise ValueError("Timeout must be between 1 and 60 seconds.")
    if method not in {"GET", "POST"}:
        raise ValueError("This client only supports GET and POST requests.")

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "DevNa-Core/0.1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    auth_token = token or _token_from_environment()
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{API_BASE}{endpoint}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise GitHubAPIError("GitHub API response exceeded the size limit.")
    except HTTPError as exc:
        if exc.code in {403, 429} and exc.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubAPIError("GitHub API rate limit reached. Wait before retrying.") from None
        safe_message = {
            401: "GitHub rejected the credentials. Check the token and its expiry.",
            403: "GitHub denied the request. Check token permissions and repository access.",
            404: "GitHub resource not found or not accessible with these permissions.",
            422: "GitHub rejected the submitted data. Check the fields and repository rules.",
        }.get(exc.code, f"GitHub API request failed with HTTP {exc.code}.")
        raise GitHubAPIError(safe_message) from None
    except URLError:
        raise GitHubAPIError("Could not connect to GitHub. Check the network and try again.") from None
    except TimeoutError:
        raise GitHubAPIError("GitHub request timed out. Try again later.") from None

    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise GitHubAPIError("GitHub returned an unexpected response format.") from None


def get_repository(repository: str, *, token: str | None = None) -> dict[str, Any]:
    """Return selected, non-secret metadata for a repository."""
    owner, name = parse_repository_slug(repository)
    data = _request(f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}", token=token)
    if not isinstance(data, dict):
        raise GitHubAPIError("GitHub returned an unexpected repository response.")
    fields = (
        "full_name", "html_url", "description", "visibility", "private",
        "default_branch", "archived", "fork", "stargazers_count", "open_issues_count",
        "language", "license",
    )
    return {key: data.get(key) for key in fields}


def list_issues(
    repository: str,
    *,
    state: str = "open",
    limit: int = 10,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """List issues, excluding pull requests from the issue endpoint's results."""
    owner, name = parse_repository_slug(repository)
    if state not in {"open", "closed", "all"}:
        raise ValueError("State must be open, closed, or all.")
    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")
    query = urlencode({"state": state, "per_page": limit, "sort": "updated", "direction": "desc"})
    data = _request(
        f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}/issues?{query}",
        token=token,
    )
    if not isinstance(data, list):
        raise GitHubAPIError("GitHub returned an unexpected issues response.")
    issues = []
    for item in data:
        if not isinstance(item, dict) or "pull_request" in item:
            continue
        issues.append({
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "html_url": item.get("html_url"),
            "updated_at": item.get("updated_at"),
            "labels": [label.get("name") for label in item.get("labels", []) if isinstance(label, dict)],
        })
    return issues


def create_issue(
    repository: str,
    *,
    title: str,
    body: str = "",
    confirmed: bool = False,
    token: str | None = None,
) -> dict[str, Any]:
    """Create an issue only after explicit confirmation and with a write token."""
    if not confirmed:
        raise ValueError("Creating a public issue requires explicit confirmation.")
    if not title.strip():
        raise ValueError("Issue title cannot be empty.")
    owner, name = parse_repository_slug(repository)
    auth_token = token or _token_from_environment()
    if not auth_token:
        raise GitHubAPIError("Set GITHUB_TOKEN or GH_TOKEN with the required repository permission.")
    data = _request(
        f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}/issues",
        method="POST",
        payload={"title": title.strip(), "body": body},
        token=auth_token,
    )
    if not isinstance(data, dict):
        raise GitHubAPIError("GitHub returned an unexpected issue response.")
    return {
        "number": data.get("number"),
        "title": data.get("title"),
        "html_url": data.get("html_url"),
        "state": data.get("state"),
    }
