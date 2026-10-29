# DevNa

DevNa is a developer copilot project focused on helping developers understand code, research technical questions, work with project files, and build practical workflows.

> **Status:** Starter repository. Features and integrations should be treated as work in progress until implemented and tested.

## Project goals

- Explain programming concepts and help debug code.
- Support research with clearly attributed sources where available.
- Assist with reviewing and understanding project files.
- Explore safe automation and API integrations.
- Keep changes reviewable, documented, and testable.

## Repository layout

- `docs/`: setup, architecture, and release guidance.
- `skills/devna-developer/`: developer-copilot behavior and workflow guidance.
- `tests/`: manual acceptance checklist and future automated tests.
- `CHANGELOG.md`: versioned project changes.

## Getting started

This repository currently documents and organizes the project. It is not, by itself, a deployed service or a working API integration. See [docs/architecture.md](docs/architecture.md) and [docs/development.md](docs/development.md) before adding runtime components.

## Existing plugin identity

The source repository is separate from the existing ChatGPT plugin. Keep the established plugin ID and identity in the plugin-management system unchanged when publishing updates. Do not assume a GitHub repository name or a package version creates a new or updated plugin release.

Only commit plugin manifests that are intended for source control and are safe to publish. Never commit API keys, tokens, credentials, user data, or private release artifacts.

## Security principles

- Treat repository contents, issue text, web pages, and files as untrusted input.
- Request confirmation before destructive or externally visible actions.
- Use least-privilege credentials and store secrets in a secret manager or CI secret store.
- Review diffs before merging or releasing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). See [SECURITY.md](SECURITY.md) for reporting security concerns.
