# DevNa public submission demo script

Record the real deployed public MCP plugin, not a mock-up. Use a screen recorder and keep the recording link accessible to reviewers without requesting access. Do not show environment variables, tokens, private repositories, private issue content, account settings, or secrets.

## Suggested 4 to 6 minute walkthrough

1. **Introduce DevNa** (15 seconds). Explain it is a public developer copilot for research, public GitHub inspection, static analysis, read-only public APIs, and safe automation planning.
2. **Web research** (45 seconds). Ask for official Python documentation about asyncio timeouts. Show the web search results, clickable URLs, and how the answer distinguishes snippets from verified source information.
3. **Repository inspection** (45 seconds). Ask for metadata and open issues for `octocat/Hello-World`. Point out the default branch, repository URL, and issue links.
4. **Read a public file** (30 seconds). Read and summarize the repository README, showing the original source link. Explain that DevNa does not execute the file.
5. **Static code analysis** (45 seconds). Submit a deliberately invalid Python snippet. Show line/column syntax diagnostics and explain that analysis does not execute the snippet.
6. **Tabular-text analysis** (30 seconds). Paste a small, fake CSV with a header and a few sample rows. Show row/column, missing-cell and distinct-value counts without returning cell contents.
7. **Allowlisted API read** (30 seconds). Ask for USD-to-EUR data using the configured Frankfurter API. Show the actual observation date from the response and the fact that the request is read-only.
8. **Safety check** (45 seconds). Ask DevNa to delete a production database. Show that it drafts a plan only and does not execute anything.
9. **Close** (15 seconds). Restate the public limitations: no private repository access, GitHub writes, arbitrary API hosts, shell execution, or scheduled background jobs.

## Before recording

- Make sure the deployed MCP URL is reachable over HTTPS.
- Confirm the service health endpoint returns `{"ok": true, ...}`.
- Connect the deployed MCP URL in ChatGPT and wait for the tool scan to finish.
- Run all five positive and three negative cases in the portal or a connected ChatGPT session.
- Confirm no tool fails or reports fictional results.
- Use only public repository sample data and fabricated CSV content.
- Do not record credentials, admin dashboards, secret settings, or personal data.
