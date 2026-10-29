"""Validate the public plugin template before building an upload ZIP."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
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
    prompts = interface.get("defaultPrompt", [])
    assert isinstance(prompts, list) and 1 <= len(prompts) <= 3
    assert all(isinstance(prompt, str) and prompt.strip() and len(prompt) <= 128 for prompt in prompts)
    capabilities = interface.get("capabilities", [])
    assert isinstance(capabilities, list) and len(capabilities) <= 20
    assert all(isinstance(item, str) and item.strip() and len(item) <= 120 for item in capabilities)
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
    skill_dirs = [item for item in (PACKAGE / "skills").iterdir() if item.is_dir()]
    assert len(skill_dirs) >= 1
    for skill_dir in skill_dirs:
        skill = skill_dir / "SKILL.md"
        assert skill.is_file(), f"Missing {skill}"
        skill_text = skill.read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)
        assert len(frontmatter) == 3 and not frontmatter[0].strip(), f"Invalid skill frontmatter: {skill}"
        fields = {}
        for line in frontmatter[1].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields.get("name", "")), f"Invalid skill name: {skill}"
        assert fields.get("description"), f"Missing skill description: {skill}"
        assert len(fields["description"]) <= 1024, f"Skill description too long: {skill}"
    for field in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        path = interface.get(field)
        assert path and (PACKAGE / path.removeprefix("./")).is_file(), f"Missing asset for {field}"
        asset = PACKAGE / path.removeprefix("./")
        assert asset.suffix.lower() == ".svg", f"Expected packaged SVG asset: {asset}"
        root = ET.parse(asset).getroot()
        assert root.tag.endswith("svg"), f"Invalid SVG root: {asset}"
        assert not any(element.tag.rsplit("}", 1)[-1].lower() in {"script", "foreignobject"} for element in root.iter()), f"Active SVG content is not allowed: {asset}"
        viewbox = root.attrib.get("viewBox", "").split()
        assert len(viewbox) == 4 and all(re.fullmatch(r"-?\d+(?:\.\d+)?", part) for part in viewbox), f"SVG needs a numeric viewBox: {asset}"
        assert float(viewbox[2]) >= 48 and float(viewbox[3]) >= 48 and float(viewbox[2]) == float(viewbox[3]), f"SVG viewBox must be square and at least 48x48: {asset}"
    servers = mcp_template.get("mcpServers", {})
    assert list(servers) == ["devna"]
    assert servers["devna"].get("type") == "streamable-http"
    assert "REPLACE-WITH-YOUR-STABLE-MCP-HOST" in servers["devna"].get("url", "")
    print("Public plugin template validation passed. Endpoint and demo recording still require deployment and a real walkthrough.")


if __name__ == "__main__":
    main()
