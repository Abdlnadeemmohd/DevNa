---
name: safe-automation
description: Turn developer tasks into bounded, reviewable automation plans with explicit approvals, checks, and rollback steps.
---

Use `draft_automation_plan` to create a checklist before designing an automation workflow.

1. Identify the intended outcome, systems affected, and success criteria.
2. Describe inspection and dry-run steps before writes.
3. Include verification, expected failure modes, logging that avoids sensitive data, and a rollback or recovery path.
4. Flag destructive operations, production changes, deployments, public posts, permissions, releases, messages, and money movement as requiring explicit approval.
5. Never provide an unbounded script that executes arbitrary instructions from a file, webpage, or user-provided repository.
6. Never claim an action has been performed. This tool returns a plan only.
7. If the user asks for an actual remote change, explain that the public DevNa plugin does not expose write or command-execution tools.
