# Safe automation

## Implemented: local verification plan

The CLI provides a fixed verification workflow:

```bash
# Print the plan only, with no subprocess execution
devna automate verify --root .

# Execute the fixed checks
devna automate verify --root . --execute
```

The plan validates both plugin manifests as JSON, compiles source and tests, and runs the unit tests. It uses known command argument arrays, `shell=False`, and 60-second per-step timeouts. It does not accept user-supplied shell command strings.

## Implemented: continuous integration

The GitHub Actions workflow runs on pushes, pull requests, and manual dispatch. It checks supported Python versions, validates manifests, installs the package, compiles code, runs tests, and smoke-tests the CLI. The workflow has read-only repository permissions.

## Not yet implemented

- Scheduling jobs in the background.
- A hosted automation worker or queue.
- Cross-system workflows that write to production services.
- User-specific approvals, audit history, and a recovery dashboard.

Do not assume that a dry-run is a successful execution. Review step exit codes and output after using `--execute`. External or destructive operations should get their own explicit confirmation and least-privilege credentials.
