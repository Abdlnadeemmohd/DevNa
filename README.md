# DevNa

DevNa is a developer-copilot project with a local Python CLI and a public MCP-server submission package in progress.

> **Status: public-release candidate, not yet published.** The CLI and MCP server pass automated CI checks. The public MCP endpoint still needs deployment, live end-to-end validation, an accessible demo recording, and submission through OpenAI's portal.

## Current components

### Public MCP server source

The server under `server/` exposes these bounded tools through MCP Streamable HTTP:

- Public web search with source links and snippets.
- Public GitHub repository metadata, issue listing, and small UTF-8 text-file reads.
- Static analysis of user-provided text, JSON, Python syntax, and logs.
- Read-only JSON GET to a server-owner allowlist of HTTPS API hosts.
- Reviewable automation planning without execution.

It intentionally does **not** access private repositories, accept user tokens, modify remote systems, execute shell commands, or run background jobs. Those capabilities require a user-authenticated design and additional security work.

### Local Python CLI

The package under `src/devna/` supports local file/project metadata inspection, GitHub repository and issue reads, explicitly confirmed issue creation, a configurable local HTTPS JSON client, and a fixed dry-run-first verification plan.

Install and run locally:

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e .
devna check
devna inspect .
devna github repo octocat/Hello-World
devna github issues octocat/Hello-World --limit 10
devna automate verify --root .
```

For private repository access or issue creation, configure a least-privilege GitHub token in `GITHUB_TOKEN` or `GH_TOKEN` locally. Never commit credentials.

## Public plugin package

The separate submission package lives in [`public-plugin/`](public-plugin/). It includes the manifest, five skills, listing icons, draft privacy/terms pages, and five positive/three negative reviewer cases. `mcp.json.template` intentionally contains a placeholder until the server has a real URL.

The final ZIP must be built after the server is deployed and a demo has actually been recorded. After merging the PR, the one-click builder is available under GitHub Actions → **Build public DevNa plugin ZIP**:

```bash
python scripts/validate_public_plugin.py
# Set DEVNA_MCP_URL and DEVNA_DEMO_RECORDING_URL first:
python scripts/build_public_plugin.py
```

Read the [public launch checklist](docs/public-launch.md). The builder refuses to package while the live HTTPS endpoint or actual demo URL is missing.

## Existing ChatGPT plugin identity

The existing private ChatGPT plugin remains **version 1.0.2** with its existing identity. OpenAI's current public-submission guidance says a server cannot be added later to an existing skills-only plugin, so the tool-enabled public version requires a separate first submission. The current private plugin is not automatically made public.

## Verification

GitHub Actions tests:
- The local CLI/package on Python 3.11, 3.12, 3.13, and 3.14.
- The public MCP server package/import and server safety tests on Python 3.13.
- Public GitHub REST read smoke test.
- Manifest and public package metadata shape.

These checks do not prove that the remote server is deployed or that the plugin has been reviewed in ChatGPT. The deployment, connected MCP scan, real end-user flow tests, identity verification, and publication are still required.

## Documentation

- [Architecture](docs/architecture.md)
- [Development workflow](docs/development.md)
- [GitHub API integration](docs/api-integration.md)
- [Automation](docs/automation.md)
- [Public release checklist](docs/public-launch.md)
- [Plugin identity and existing-release workflow](docs/plugin-identity.md)
- [Security policy](SECURITY.md)
