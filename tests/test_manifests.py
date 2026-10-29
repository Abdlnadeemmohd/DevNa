from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_plugin_manifests_are_valid_and_aligned(self):
        standard = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(standard["name"], "devna")
        self.assertEqual(codex["name"], "devna")
        self.assertEqual(standard["version"], codex["version"])
        self.assertEqual(standard["version"], "1.0.2")
        self.assertEqual(codex["interface"]["displayName"], "DevNa")

    def test_public_manifests_do_not_embed_private_plugin_identity_or_email(self):
        for path in (ROOT / "plugin.json", ROOT / ".codex-plugin" / "plugin.json"):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("plugins_", content)
            self.assertNotIn("pluginrel_", content)
            self.assertNotIn('"email"', content)


if __name__ == "__main__":
    unittest.main()
