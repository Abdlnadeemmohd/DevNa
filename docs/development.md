# Development workflow

## Working locally

1. Clone this repository.
2. Create a short-lived feature branch.
3. Make one focused change at a time.
4. Run the checks relevant to the changed files.
5. Review the full diff for secrets and unintended changes.
6. Open a pull request with verification steps.

No runtime language or test framework has been selected in this starter scaffold, so there are not yet project-specific build commands.

## Configuration

Use environment variables or a secrets manager for credentials. Keep a sanitized `.env.example` if configuration examples become necessary. Never place live values in that file.

## Release discipline

- Update `CHANGELOG.md` for user-visible changes.
- Validate manifests and tests before packaging.
- Make the release version and compatibility expectations explicit.
- Treat plugin package upload and plugin release publication as separate actions that require verification.
