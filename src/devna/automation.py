"""A fixed, reviewable local verification plan. No arbitrary command execution."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def build_verification_plan(root: str | Path) -> list[dict[str, Any]]:
    """Create a fixed command list; callers cannot inject arbitrary shell commands."""
    project_root = Path(root).resolve()
    python = sys.executable
    return [
        {
            "name": "validate primary plugin manifest",
            "command": [python, "-m", "json.tool", "plugin.json"],
            "cwd": str(project_root),
        },
        {
            "name": "validate Codex plugin manifest",
            "command": [python, "-m", "json.tool", ".codex-plugin/plugin.json"],
            "cwd": str(project_root),
        },
        {
            "name": "compile source and tests",
            "command": [python, "-m", "compileall", "-q", "src", "tests"],
            "cwd": str(project_root),
        },
        {
            "name": "run unit tests",
            "command": [python, "-m", "unittest", "discover", "-s", "tests", "-v"],
            "cwd": str(project_root),
        },
    ]


def run_verification(root: str | Path, *, execute: bool = False) -> dict[str, Any]:
    """Return a plan by default. Execute only the fixed allowlisted checks on request."""
    plan = build_verification_plan(root)
    if not execute:
        return {
            "mode": "dry_run",
            "message": "Nothing was executed. Add --execute to run these fixed checks.",
            "steps": [
                {"name": step["name"], "command": step["command"]}
                for step in plan
            ],
        }

    results = []
    for step in plan:
        try:
            completed = subprocess.run(
                step["command"],
                cwd=step["cwd"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            results.append({
                "name": step["name"],
                "return_code": completed.returncode,
                "passed": completed.returncode == 0,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            })
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({
                "name": step["name"],
                "passed": False,
                "error": type(exc).__name__,
            })
    return {
        "mode": "executed",
        "passed": all(result.get("passed", False) for result in results),
        "steps": results,
    }
