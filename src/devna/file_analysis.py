"""Metadata-first local project inspection without executing project code."""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", "coverage",
}
SENSITIVE_NAMES = {
    ".env", ".netrc", ".npmrc", ".pypirc", "id_rsa", "id_ed25519",
    "credentials.json", "secrets.json",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
MAX_TEXT_BYTES = 1_000_000
MAX_DIRECTORY_FILES = 5000


def is_sensitive_path(path: Path) -> bool:
    name = path.name.lower()
    return (
        name in SENSITIVE_NAMES
        or name.startswith(".env.")
        or path.suffix.lower() in SENSITIVE_SUFFIXES
    )


def _file_record(path: Path, display_path: str, *, read_text: bool) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError:
        return {"path": display_path, "error": "File metadata could not be read."}

    record: dict[str, Any] = {
        "path": display_path,
        "size_bytes": stat.st_size,
        "extension": path.suffix.lower() or "[no extension]",
        "sensitive_filename": is_sensitive_path(path),
    }
    if not read_text or is_sensitive_path(path) or stat.st_size > MAX_TEXT_BYTES:
        record["content_inspected"] = False
        return record

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        record["content_inspected"] = False
        record["text_note"] = "Not read as UTF-8 text."
        return record

    record["content_inspected"] = True
    record["line_count"] = len(text.splitlines())
    if path.suffix.lower() == ".json":
        try:
            json.loads(text)
            record["valid_json"] = True
        except json.JSONDecodeError:
            record["valid_json"] = False
    return record


def analyze_path(value: str | Path) -> dict[str, Any]:
    """Inspect a file or directory while skipping common build folders and secrets."""
    raw_path = Path(value).expanduser()
    if raw_path.is_symlink():
        raise ValueError("Refusing to inspect a symbolic link.")
    if not raw_path.exists():
        raise ValueError("The requested path does not exist.")
    root = raw_path.resolve()
    if root.is_file():
        return {
            "kind": "file",
            "root": str(root),
            "file": _file_record(root, root.name, read_text=True),
        }
    if not root.is_dir():
        raise ValueError("The requested path is not a regular file or directory.")

    extension_counts: Counter[str] = Counter()
    total_bytes = 0
    total_files = 0
    sensitive_files = 0
    examples: list[dict[str, Any]] = []
    truncated = False

    for current, dirs, filenames in os.walk(root, followlinks=False):
        dirs[:] = [
            name for name in dirs
            if name not in IGNORED_DIRS and not (Path(current) / name).is_symlink()
        ]
        for filename in filenames:
            path = Path(current) / filename
            if path.is_symlink() or not path.is_file():
                continue
            total_files += 1
            try:
                total_bytes += path.stat().st_size
            except OSError:
                pass
            extension_counts[path.suffix.lower() or "[no extension]"] += 1
            sensitive_files += int(is_sensitive_path(path))
            if len(examples) < 100:
                examples.append(_file_record(path, str(path.relative_to(root)), read_text=False))
            if total_files >= MAX_DIRECTORY_FILES:
                truncated = True
                break
        if truncated:
            break

    return {
        "kind": "directory",
        "root": str(root),
        "files_counted": total_files,
        "total_size_bytes": total_bytes,
        "sensitive_filenames_skipped": sensitive_files,
        "extension_counts": dict(sorted(extension_counts.items())),
        "file_examples": examples,
        "file_examples_truncated": total_files > len(examples),
        "scan_limit_reached": truncated,
        "note": "Directory inspection reports metadata only; it does not execute project files.",
    }
