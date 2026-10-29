from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from devna.file_analysis import analyze_path, is_sensitive_path


class FileAnalysisTests(unittest.TestCase):
    def test_sensitive_names_are_recognized(self):
        self.assertTrue(is_sensitive_path(Path(".env")))
        self.assertTrue(is_sensitive_path(Path(".env.production")))
        self.assertTrue(is_sensitive_path(Path("private.pem")))
        self.assertFalse(is_sensitive_path(Path("README.md")))

    def test_directory_scan_skips_secret_content_and_build_folders(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src").mkdir()
            (root / "node_modules").mkdir()
            (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=should-not-be-read", encoding="utf-8")
            (root / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
            result = analyze_path(root)
            self.assertEqual(result["files_counted"], 2)
            self.assertEqual(result["sensitive_filenames_skipped"], 1)
            self.assertNotIn("TOKEN=should-not-be-read", json.dumps(result))
            self.assertNotIn("ignored.js", json.dumps(result))

    def test_file_inspection_counts_lines_and_validates_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config.json"
            path.write_text('{"ok": true}\n', encoding="utf-8")
            result = analyze_path(path)
            self.assertEqual(result["kind"], "file")
            self.assertTrue(result["file"]["valid_json"])
            self.assertEqual(result["file"]["line_count"], 1)

    def test_missing_path_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "does not exist"):
                analyze_path(Path(temp) / "missing.txt")


if __name__ == "__main__":
    unittest.main()
