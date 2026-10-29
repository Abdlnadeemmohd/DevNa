# Acceptance checklist

This checklist tracks end-to-end readiness. Unit tests cover the implemented parts, but production readiness requires additional validation.

## Implemented in the current CLI

- [x] Local command-line entry point and version output.
- [x] Local file and directory metadata inspection.
- [x] Sensitive filenames are identified; their contents are not read into output.
- [x] Common generated and dependency directories are skipped.
- [x] Read repository metadata through the fixed GitHub API host.
- [x] List issues and exclude pull requests returned by the issues endpoint.
- [x] Require explicit confirmation and a configured token before creating a GitHub issue.
- [x] Dry-run mode for fixed verification automation.
- [x] Automated unit tests for API response handling, safety checks, and automation.

## Must pass before release

- [x] All unit tests pass on supported Python versions (3.11, 3.12, 3.13, and 3.14).
- [x] Package installs successfully in a clean environment via CI.
- [x] CI run succeeds for a branch push and pull request.
- [ ] Verify GitHub API reads against a real public repository.
- [ ] Verify private-repository access using a least-privilege test token without exposing it.
- [ ] Verify issue creation only in a dedicated test repository and only with explicit approval.
- [ ] Review error behavior for network failures, API rate limits, expired credentials, and insufficient permissions.
- [ ] Review public commits for accidentally included secrets and personal data.
- [ ] Verify supported Python versions and platform behavior.

## Not yet implemented or not yet validated

- [ ] Web research engine with source ranking and citations.
- [ ] General-purpose document parsing for PDF, DOCX, spreadsheets, and archives.
- [ ] Hosted API service, authentication, per-user authorization, and deployment.
- [ ] Multi-user GitHub App or OAuth integration.
- [ ] Scheduled or background automation service.
- [ ] Full plugin runtime test matrix.
- [ ] Production security review and release process.
