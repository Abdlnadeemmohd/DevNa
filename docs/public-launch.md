# Public release checklist for DevNa

This guide prepares the remote-MCP version for a new public directory submission. It does not publish anything automatically.

## Why a separate public submission package

The existing ChatGPT plugin is a private, skills-only plugin at version 1.0.2. OpenAI's current submission documentation says an MCP server cannot be added later to an existing skills-only plugin. The public tool-enabled edition therefore needs its own initial submission package and public listing. Keep the existing private plugin intact.

## Current implementation

The public MCP service in `server/main.py` exposes bounded, read-mostly tools:
- `web_search`
- `github_get_repository`
- `github_list_issues`
- `github_read_file`
- `analyze_text_file`
- `fetch_allowlisted_api_json`
- `draft_automation_plan`

It intentionally has no private-repository access, write operations, arbitrary shell execution, or scheduled background jobs. Those features need user-specific authentication and a larger security review before they belong in a public unauthenticated server.

## Deployment and cost control

1. Read `server/README.md` and inspect `render.yaml`.
2. Open Render, connect this GitHub repository, and create a Blueprint using the feature branch for initial testing.
3. Review the service plan, billing, and current provider terms before creating any service. The current blueprint selects a starter service to avoid a sleep-prone public endpoint. Do not create a paid service unless you approve the cost.
4. Deploy the service, then check `/healthz`.
5. Test the Streamable HTTP MCP endpoint at `/mcp` with a compatible MCP client and manually test each positive/negative case in the package manifest.
6. In the OpenAI plugin portal, create the public submission draft and connect the endpoint. Complete any domain-verification challenge by setting the exact token as the private `OPENAI_APPS_CHALLENGE` hosting environment variable. Never commit the token.
7. Confirm the server's configured API allowlist. The default list contains `api.github.com` and `api.frankfurter.app`. Only add hosts you trust and intend to support.

## Build the upload ZIP

The public package manifest, skills, listing icon, privacy-policy draft, terms draft, and reviewer test cases are under `public-plugin/`.

Record an accessible walkthrough video only after the live service has been tested. Then set these variables in your terminal:

- `DEVNA_MCP_URL`: the deployed stable HTTPS endpoint ending in `/mcp`.
- `DEVNA_DEMO_RECORDING_URL`: HTTPS link to the actual reviewer-accessible walkthrough video.

Run:

```bash
python scripts/validate_public_plugin.py
python scripts/build_public_plugin.py
```

The builder checks the live `/healthz` endpoint, injects the actual MCP and demo URLs, and writes `dist/devna-public-1.0.0.zip`. Do not hand-edit the packaged endpoint after validation. Inspect the ZIP and the final manifest before uploading.

## OpenAI public submission steps

1. Open the [Plugins submission portal](https://platform.openai.com/plugins) and choose the verified developer identity that will publish DevNa.
2. Upload `dist/devna-public-1.0.0.zip` as a new submission. The existing private plugin remains separate.
3. Wait for package/skill scans. Connect the MCP server, complete domain verification and authentication setup, and inspect every discovered tool.
4. Run all five positive and three negative test cases against the live tool set. Replace any inaccurate examples and re-upload the package if needed.
5. Complete the policy attestations and submit for review. Review approval is controlled by OpenAI, not this repository.
6. After approval, choose **Publish plugin** in the portal.

Do not claim public availability until the portal confirms that publication is complete.

## Publisher-owned tasks that cannot be safely automated from this repository

- Create the Render service in your account and approve any billing.
- Keep the public service available and monitor logs/usage.
- Record the actual demo walkthrough and provide its URL.
- Complete individual/business identity verification and legal/policy attestations.
- Upload the package, connect the server, run portal-side tests, and submit for review.
- Publish only after approval.

## Reference material

- [OpenAI package guide](https://developers.openai.com/plugins/build/plugins)
- [OpenAI MCP server guide](https://developers.openai.com/plugins/build/mcp-server)
- [OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission)
- [OpenAI plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines)
