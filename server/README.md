# DevNa Public MCP Server

This service exposes read-mostly developer tools over MCP Streamable HTTP. It is designed for a public directory submission, but must be deployed to a stable public HTTPS endpoint and tested before the plugin ZIP is submitted.

## Tools

- `web_search`: metasearch with titles, source URLs, and snippets.
- `github_get_repository`: public GitHub repository metadata.
- `github_list_issues`: issues in a public repository, excluding pull requests.
- `github_read_file`: small UTF-8 text files from public repositories; does not execute content.
- `analyze_text_file`: static analysis for pasted text, JSON, Python syntax, and logs; does not echo or execute content.
- `fetch_allowlisted_api_json`: read-only HTTPS JSON GET against the server's configured allowlist.
- `draft_automation_plan`: proposes a safe plan without executing commands or changing systems.

The service does not accept caller-supplied GitHub tokens, modify GitHub repositories, execute shell commands, or support arbitrary URLs/API hosts. These limits are intentional for an unauthenticated public service. Private repository access and write actions require a user-authenticated OAuth/GitHub App design before adding them.

## Local run

Requires Python 3.11+.

```bash
python -m venv .venv
# Activate it
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

MCP endpoint: `http://127.0.0.1:8000/mcp`
Health endpoint: `http://127.0.0.1:8000/healthz`

## Render deployment

1. In Render, create a new Blueprint from this repository.
2. Select branch `feature/devna-core-runtime` for initial testing. After the pull request is merged, update the service to the chosen release branch.
3. Review the `render.yaml` service plan and costs before creating it.
4. Wait for deployment to be healthy.
5. Verify `https://YOUR-SERVICE.onrender.com/healthz` and use an MCP client to enumerate and test tools at `https://YOUR-SERVICE.onrender.com/mcp`.
6. Replace the placeholder in `public-plugin/mcp.json.template` with the actual stable HTTPS endpoint, then create the upload ZIP.

The service name can be unavailable or changed by Render. Do not upload the plugin package while its MCP URL still contains a placeholder.

## Security notes

- Keep tool inputs bounded and output content trimmed.
- API requests use a strict host allowlist and disable redirects.
- Do not add secrets to this repository or its deployment manifest.
- Public service operators may incur hosting or metasearch usage costs. Review current provider terms and limits before launch.
- Before publication, complete the privacy policy and terms review, test the service through ChatGPT, and prepare an accessible demo recording.
