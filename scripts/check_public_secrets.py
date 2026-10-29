"""Fail if sensitive tokens or private plugin backend IDs enter the public release payload."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (ROOT / "public-plugin", ROOT / "server")
PATTERNS = {
    "GitHub personal-access token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    "OpenAI-style secret key": re.compile(r"\bsk-[A-Za-z0-9_-]{30,}\b"),
    "private key material": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    "private plugin backend ID": re.compile(r"\bplugins_[0-9a-f]{20,}\b"),
    "private plugin release ID": re.compile(r"\bpluginrel_[0-9a-f]{20,}\b"),
}


def main() -> int:
    issues: list[str] = []
    files_scanned = 0
    for target in TARGETS:
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            files_scanned += 1
            for label, pattern in PATTERNS.items():
                match = pattern.search(text)
                if match:
                    issues.append(f"{path.relative_to(ROOT)}: possible {label}")
    if issues:
        print("Public payload secret scan failed:")
        print("\n".join(f"- {issue}" for issue in issues))
        return 1
    print(f"Public payload secret scan passed ({files_scanned} text files checked).")
    print("This scan checks current file contents only; it does not scan Git history or deployment logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
