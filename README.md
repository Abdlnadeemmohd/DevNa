# DevNa

DevNa is a developer-copilot project. This repository now contains an early **Python command-line toolkit** for local project inspection, GitHub REST API reads, explicitly confirmed issue creation, and repeatable verification checks.

> **Status: alpha.** This is a working starter implementation, not a hosted AI service. Features should be treated as supported only to the extent described and tested here.

## What is implemented

- Inspect local files and project directories without executing their contents.
- Read repository metadata and list GitHub issues through the GitHub REST API.
- Create a GitHub issue only when explicitly confirmed on the command line and a suitable token is configured.
- Preview a fixed set of local verification commands. Execution is opt-in.
- Run unit tests and manifest checks in GitHub Actions.

## Requirements

- Python 3.11 or later.
- A GitHub token is optional for public repository reads.
- For private repository reads or issue creation, use a fine-grained token with only the required repository permissions.

## Install locally

From the repository root:

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e .
devna check
```

On Windows, activate with `.venv\\Scripts\\activate`. On macOS/Linux, use `source .venv/bin/activate`.

## Common commands

```bash
# Show version and local configuration state
devna check

# Inspect a file or directory (does not execute project code)
devna inspect .

# Read public repository metadata
devna github repo octocat/Hello-World

# List open issues
devna github issues octocat/Hello-World --limit 10

# Preview the fixed verification workflow
devna automate verify --root .

# Run manifest validation, compilation, and unit tests
devna automate verify --root . --execute
```

For issue creation, configure `GITHUB_TOKEN` or `GH_TOKEN` in your shell and request the write explicitly:

```bash
devna github create-issue OWNER/REPO --title "Bug report" --body "Describe the problem." --confirm-public-write
```

Issue creation needs the token's Issues write permission. Treat it as a public, externally visible action and check the repository before confirming it.

## Documentation

- [Architecture](docs/architecture.md)
- [Development workflow](docs/development.md)
- [GitHub API integration](docs/api-integration.md)
- [Safe automation](docs/automation.md)
- [Plugin identity and releases](docs/plugin-identity.md)
- [Security policy](SECURITY.md)
- [Acceptance checklist](tests/ACCEPTANCE_CHECKLIST.md)

## ChatGPT plugin identity

The source repository is separate from the existing ChatGPT plugin. The existing plugin is managed by the plugin platform and remains private. A repository commit or package version does not prove that a plugin release has been uploaded or published. Follow [the identity and release guide](docs/plugin-identity.md) when packaging updates.

## Security

Never commit tokens, keys, or production data. The CLI does not print token values. For a public multi-user application, use a proper GitHub App or OAuth flow rather than asking every user to share a developer's token. See [SECURITY.md](SECURITY.md).

## License

No open-source license has been selected for this repository yet. Do not assume the source is licensed for reuse until a license is deliberately added.
