# Architecture

## Current implementation

The repository contains an early Python CLI package under `src/devna/`. It currently provides:
- A command-line entry point.
- A GitHub REST API client restricted to the fixed `api.github.com` host.
- Metadata-first inspection of local files and folders.
- A predefined verification plan that defaults to dry-run.
- Unit tests and CI validation.

It is not a hosted AI model, web application, database-backed service, or background worker.

## Logical components

1. **CLI:** parses user intent and prints structured JSON results.
2. **GitHub client:** reads repository metadata and issues; issue creation requires a token and explicit confirmation.
3. **File inspection:** reports metadata and selected text-file characteristics without executing project code. Directory scans skip common build folders and do not read sensitive filenames.
4. **Verification automation:** exposes a fixed list of checks. It does not accept arbitrary shell commands from users.
5. **Tests and CI:** unit tests run with Python's standard library; GitHub Actions validates manifests, syntax, tests, and package installation.

## Trust boundaries

- Local project files, web content, issue text, and API responses are untrusted input.
- Tokens must come from environment variables or a secret manager and must never be committed.
- Write operations must remain explicit and auditable.
- The local inspector does not execute source files.
- The GitHub API client does not accept arbitrary API hosts or methods outside its supported allowlist.

## Future work

A hosted, multi-user DevNa product would need an authenticated server, per-user authorization, an appropriate GitHub App/OAuth flow, rate limiting, audit logging, deployment configuration, and privacy controls. None of those are implied by this CLI starter.
