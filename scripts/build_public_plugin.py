"""Build a public-directory ZIP only after a real MCP deployment and demo exist.

Required environment variables:
  DEVNA_MCP_URL=https://your-stable-service.example/mcp
  DEVNA_DEMO_RECORDING_URL=https://your-accessible-demo.example/...
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "public-plugin"
OUTPUT = ROOT / "dist" / "devna-public-1.0.0.zip"


def require_https(value: str, label: str, *, allow_query_fragment: bool = False) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or (not allow_query_fragment and (parsed.query or parsed.fragment))
    ):
        suffix = " without credentials, query, or fragment" if not allow_query_fragment else " without embedded credentials"
        raise SystemExit(f"{label} must be a valid HTTPS URL{suffix}.")
    # Video hosts commonly encode the recording ID in a query parameter. Preserve that URL
    # exactly; only normalize a trailing slash for the MCP endpoint.
    return value if allow_query_fragment else value.rstrip("/")


def verify_endpoint(mcp_url: str) -> None:
    if not mcp_url.endswith("/mcp"):
        raise SystemExit("DEVNA_MCP_URL must end in /mcp.")
    parsed = urlsplit(mcp_url)
    health_url = f"{parsed.scheme}://{parsed.netloc}/healthz"
    request = urllib.request.Request(health_url, headers={"User-Agent": "DevNa-Package-Builder/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            if response.status != 200:
                raise SystemExit(f"Health check failed with status {response.status}.")
            body = response.read(4096).decode("utf-8", "replace")
            payload = json.loads(body)
            if payload.get("ok") is not True:
                raise SystemExit("Health endpoint did not return ok=true.")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise SystemExit(f"Could not verify the deployed MCP service: {type(exc).__name__}.") from None


def main() -> int:
    mcp_url = os.environ.get("DEVNA_MCP_URL", "").strip()
    demo_url = os.environ.get("DEVNA_DEMO_RECORDING_URL", "").strip()
    if not mcp_url or not demo_url:
        raise SystemExit("Set both DEVNA_MCP_URL and DEVNA_DEMO_RECORDING_URL before building the upload ZIP.")
    mcp_url = require_https(mcp_url, "DEVNA_MCP_URL")
    demo_url = require_https(demo_url, "DEVNA_DEMO_RECORDING_URL", allow_query_fragment=True)
    verify_endpoint(mcp_url)

    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_public_plugin.py")], check=True)
    manifest = json.loads((PACKAGE / "plugin.json").read_text(encoding="utf-8"))
    ext = manifest.setdefault("extensions", {}).setdefault("com.openai", {})
    ext.setdefault("review", {})["demo_recording_url"] = demo_url

    template = json.loads((PACKAGE / "mcp.json.template").read_text(encoding="utf-8"))
    template["mcpServers"]["devna"]["url"] = mcp_url
    if "REPLACE-" in mcp_url or ".invalid" in mcp_url:
        raise SystemExit("MCP URL still looks like a placeholder.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("plugin.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        archive.writestr("mcp.json", json.dumps(template, ensure_ascii=False, indent=2) + "\n")
        for path in PACKAGE.rglob("*"):
            if not path.is_file() or path.name == "plugin.json" or path.name == "mcp.json.template":
                continue
            if "__pycache__" in path.parts or path.suffix in {".pyc"}:
                continue
            archive.write(path, path.relative_to(PACKAGE).as_posix())
    with zipfile.ZipFile(OUTPUT, "r") as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise SystemExit(f"ZIP integrity check failed at {bad_member}.")
        names = set(archive.namelist())
        if "mcp.json" not in names or "mcp.json.template" in names:
            raise SystemExit("ZIP must contain the generated mcp.json and exclude its template.")
        packed_manifest = json.loads(archive.read("plugin.json").decode("utf-8"))
        packed_review = packed_manifest["extensions"]["com.openai"]["review"]
        if not packed_review.get("demo_recording_url"):
            raise SystemExit("The upload ZIP does not contain the real demo recording URL.")
    print(f"Built {OUTPUT}")
    print("Review the contents and run the positive/negative cases against the live service before upload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
