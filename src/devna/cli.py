"""Command-line entry point for DevNa core."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from devna import __version__
from devna.automation import run_verification
from devna.file_analysis import analyze_path
from devna.github_api import GitHubAPIError, create_issue, get_repository, list_issues


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devna",
        description="Beginner-friendly developer tooling with safe, explicit GitHub actions.",
    )
    parser.add_argument("--version", action="version", version=f"DevNa Core {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="show local runtime and configuration status")

    inspect_parser = subparsers.add_parser("inspect", help="inspect local file or project metadata")
    inspect_parser.add_argument("path", nargs="?", default=".", help="file or directory to inspect")

    github_parser = subparsers.add_parser("github", help="interact with the GitHub REST API")
    github_subparsers = github_parser.add_subparsers(dest="github_command", required=True)

    repo_parser = github_subparsers.add_parser("repo", help="read repository metadata")
    repo_parser.add_argument("repository", help="repository in OWNER/REPO format")

    issues_parser = github_subparsers.add_parser("issues", help="list repository issues")
    issues_parser.add_argument("repository", help="repository in OWNER/REPO format")
    issues_parser.add_argument("--state", choices=("open", "closed", "all"), default="open")
    issues_parser.add_argument("--limit", type=int, default=10)

    create_parser = github_subparsers.add_parser("create-issue", help="create a repository issue")
    create_parser.add_argument("repository", help="repository in OWNER/REPO format")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--body", default="")
    create_parser.add_argument(
        "--confirm-public-write",
        action="store_true",
        help="confirm the issue should be created on GitHub",
    )

    automate_parser = subparsers.add_parser("automate", help="preview or run fixed local checks")
    automate_subparsers = automate_parser.add_subparsers(dest="automation_command", required=True)
    verify_parser = automate_subparsers.add_parser("verify", help="run manifest, compile, and unit checks")
    verify_parser.add_argument("--root", default=".", help="repository root directory")
    verify_parser.add_argument(
        "--execute",
        action="store_true",
        help="execute the fixed checks; without this flag, only show the plan",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "check":
            _print_json({
                "product": "DevNa Core",
                "version": __version__,
                "python": platform.python_version(),
                "github_token_configured": bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")),
                "supported_features": [
                    "local metadata inspection",
                    "GitHub repository and issue reads",
                    "explicitly confirmed GitHub issue creation",
                    "dry-run verification plan",
                ],
                "note": "This is a local toolkit, not a hosted AI model or web service.",
            })
            return 0

        if args.command == "inspect":
            _print_json(analyze_path(args.path))
            return 0

        if args.command == "github":
            if args.github_command == "repo":
                _print_json(get_repository(args.repository))
                return 0
            if args.github_command == "issues":
                _print_json({
                    "repository": args.repository,
                    "state": args.state,
                    "issues": list_issues(args.repository, state=args.state, limit=args.limit),
                })
                return 0
            if args.github_command == "create-issue":
                result = create_issue(
                    args.repository,
                    title=args.title,
                    body=args.body,
                    confirmed=args.confirm_public_write,
                )
                _print_json({
                    **result,
                    "note": "Issue creation was requested with explicit confirmation.",
                })
                return 0

        if args.command == "automate" and args.automation_command == "verify":
            result = run_verification(Path(args.root), execute=args.execute)
            _print_json(result)
            return 0 if result.get("mode") == "dry_run" or result.get("passed") else 1

        _print_json({"error": "Unsupported command."})
        return 2
    except (ValueError, GitHubAPIError, OSError) as exc:
        _print_json({"error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
