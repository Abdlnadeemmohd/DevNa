from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch, Mock

from devna.automation import build_verification_plan, run_verification


class AutomationTests(unittest.TestCase):
    def test_plan_contains_only_fixed_commands(self):
        plan = build_verification_plan(".")
        self.assertEqual(len(plan), 4)
        self.assertTrue(all(isinstance(step["command"], list) for step in plan))
        self.assertTrue(all(step["command"][0] for step in plan))

    @patch("devna.automation.subprocess.run")
    def test_default_mode_is_dry_run(self, mock_run):
        result = run_verification(".", execute=False)
        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(len(result["steps"]), 4)
        mock_run.assert_not_called()

    @patch("devna.automation.subprocess.run")
    def test_execute_runs_without_shell_and_reports_status(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="ok", stderr="")
        result = run_verification(".", execute=True)
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["steps"]), 4)
        self.assertTrue(all(call.kwargs["shell"] is False for call in mock_run.call_args_list))

    @patch("devna.automation.subprocess.run")
    def test_failed_check_makes_workflow_fail(self, mock_run):
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),
            Mock(returncode=0, stdout="", stderr=""),
            Mock(returncode=1, stdout="", stderr="compile error"),
            Mock(returncode=0, stdout="", stderr=""),
        ]
        result = run_verification(".", execute=True)
        self.assertFalse(result["passed"])
        self.assertFalse(result["steps"][2]["passed"])


if __name__ == "__main__":
    unittest.main()
