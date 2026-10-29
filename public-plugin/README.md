# DevNa Public Copilot

This folder is the **public-directory submission package template** for DevNa. It is separate from the existing private ChatGPT plugin.

## Included capabilities

- Web search with result URLs and snippets.
- Public GitHub repository metadata, issue listing, and small UTF-8 file reads.
- Static analysis of user-provided JSON, Python snippets, text, logs, and CSV/TSV structure.
- Read-only JSON GET requests to a server-owner allowlist of HTTPS API hosts.
- Reviewable automation plans that do not execute commands.

## Intentionally excluded

The public server does not accept user-provided GitHub credentials, access private repositories, create or modify issues, write to arbitrary APIs, execute shell commands, deploy software, or run background jobs. Those features would need an appropriately authenticated and authorized design.

## Do not upload the template as-is

The file `mcp.json.template` has a placeholder endpoint. The final upload package must be built only after:
1. Deploying the server at a stable HTTPS endpoint.
2. Verifying `/healthz` and testing MCP tools at `/mcp`.
3. Running the positive and negative test cases against the live endpoint.
4. Recording an accessible demo walkthrough.
5. Completing developer identity verification and reviewing the privacy/terms drafts.
5. Reviewing the privacy policy and terms.

From the repository root, the release builder requires the live MCP and demo URLs:

```bash
python scripts/build_public_plugin.py
```

Set `DEVNA_MCP_URL` and `DEVNA_DEMO_RECORDING_URL` in your shell before running it. The builder performs an HTTPS health check and will refuse placeholder endpoints.

OpenAI's public directory requires verified publisher identity, successful automated checks, an accessible demo for remote MCP submission, and review approval. A successful package build does not publish the plugin.
