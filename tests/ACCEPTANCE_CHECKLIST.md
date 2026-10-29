# Acceptance checklist

## Verified in CI

- [x] Local CLI package installs, compiles, and runs its unit tests on Python 3.11, 3.12, 3.13, and 3.14.
- [x] Plugin source manifests are valid JSON and aligned.
- [x] Public package template manifest and listing metadata validate.
- [x] Public MCP server imports on Python 3.13.
- [x] Public MCP server safety tests pass.
- [x] GitHub public repository metadata can be read by the CLI smoke test.
- [x] Public package includes five positive and three negative test cases.
- [x] Package builder refuses to build without both the deployed MCP URL and an actual demo URL.
- [x] Server provides a configurable plain-text domain challenge route for the OpenAI publishing portal.
- [x] Existing private plugin was updated in place to v1.0.2 and its identity and private visibility were re-verified.

## Required before public submission

- [ ] Deploy the MCP server at a stable public HTTPS host under the publisher's account.
- [ ] Verify `/healthz` and test Streamable HTTP at `/mcp` using an MCP client.
- [ ] Configure and verify the final allowed API host list.
- [ ] Test web search against live sources and confirm errors/rate-limit behavior.
- [ ] Test live GitHub repository metadata, issue listing, and small file reads from ChatGPT via the connected MCP server.
- [ ] Test static text/JSON/Python analysis and safe automation planning via ChatGPT.
- [ ] If the portal requests domain verification, set `OPENAI_APPS_CHALLENGE` through the hosting dashboard and verify the exact plain-text response.
- [ ] Record an accessible demo video showing real positive and negative use cases.
- [ ] Review the privacy policy and terms against the actual host/search providers and intended operating jurisdictions.
- [ ] Complete publisher identity verification and policy attestations in the OpenAI Platform.
- [ ] Build the final ZIP by setting `DEVNA_MCP_URL` and `DEVNA_DEMO_RECORDING_URL`; inspect its contents and upload it to the public submission portal.
- [ ] Run all five positive and three negative test cases against the live endpoint in the portal.
- [ ] Submit for review, resolve findings, receive approval, and then select Publish.

## Not implemented in the public server

- [ ] OAuth/GitHub App authentication for private repository access.
- [ ] GitHub issue/PR/repository writes.
- [ ] General API write actions.
- [ ] Shell execution, deployments, or background scheduling.
- [ ] Full PDF, DOCX, and spreadsheet parsing in the MCP server.
- [ ] Production monitoring/abuse controls review beyond bounded inputs and fixed API allowlists.

A green CI run is necessary but not sufficient for public launch.
