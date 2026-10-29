"""Validate the public plugin template before building an upload ZIP."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "public-plugin"


def main() -> None:
    manifest_path = PACKAGE / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mcp_template = json.loads((PACKAGE / "mcp.json.template").read_text(encoding="utf-8"))
    extension = manifest.get("extensions", {}).get("com.openai", {})
    interface = extension.get("interface", {})
    review = extension.get("review", {})
    cases = review.get("test_cases", {})
    positive = cases.get("positive", [])
    negative = cases.get("negative", [])

    assert manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest.get("name", ""))
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", ""))
    assert interface.get("displayName") and len(interface["displayName"]) <= 30
    assert interface.get("shortDescription") and len(interface["shortDescription"]) <= 30
    assert interface.get("longDescription") and len(interface["longDescription"]) <= 4000
    assert interface.get("developerName") and len(interface["developerName"]) <= 80
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        assert interface.get(key, "").startswith("https://"), f"{key} must be HTTPS"
    assert len(positive) == 5, "Remote MCP review requires exactly five positive cases."
    assert len(negative) == 3, "Remote MCP review requires exactly three negative cases."
    required_positive = ("description", "prompt", "tools_triggered", "expected_behavior")
    required_negative = ("description", "prompt")
    for item in positive:
        assert all(isinstance(item.get(key), str) and item[key].strip() for key in required_positive)
    for item in negative:
        assert all(isinstance(item.get(key), str) and item[key].strip() for key in required_negative)
    assert extension.get("onboardingSkill") == "./skills/devna-developer/SKILL.md"
    assert (PACKAGE / "skills/devna-developer/SKILL.md").is_file()
    for skill_dir in (PACKAGE / "skills").iterdir():
        if skill_dir.is_dir():
            skill = skill_dir / "SKILL.md"
            assert skill.is_file(), f"Missing {skill}"
    for field in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        path = interface.get(field)
        assert path and (PACKAGE / path.removeprefix("./")).is_file(), f"Missing asset for {field}"
    servers = mcp_template.get("mcpServers", {})
    assert list(servers) == ["devna"]
    assert servers["devna"].get("type") == "streamable-http"
    assert "REPLACE-WITH-YOUR-STABLE-MCP-HOST" in servers["devna"].get("url", "")
    print("Public plugin template validation passed. Endpoint and demo recording still require deployment and a real walkthrough.")


if __name__ == "__main__":
    main()
