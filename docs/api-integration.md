# GitHub API integration

## Implemented operations

The local CLI uses Python's standard library and the fixed `https://api.github.com` host.

- `devna github repo OWNER/REPO`: read selected repository metadata.
- `devna github issues OWNER/REPO --state open --limit 10`: list issues, excluding pull requests.
- `devna github create-issue OWNER/REPO --title "..." --body "..." --confirm-public-write`: create an issue only after explicit confirmation.

The read commands can work against public repositories without a token. Rate limits still apply.

## Tokens

For private repository access or issue creation, set a token in your shell:

Linux/macOS:
```bash
export GITHUB_TOKEN="YOUR_TOKEN"
```

PowerShell:
```powershell
$env:GITHUB_TOKEN = "YOUR_TOKEN"
```

DevNa also accepts `GH_TOKEN`. Never type a live token into a source file, command committed to shell history, issue, or chat. Prefer your operating system's secure secret storage for ongoing use.

Use a fine-grained token scoped to the specific repository. Read operations should have only the metadata and issue read permissions they need. Issue creation requires Issues write permission. The exact permissions should be verified against the current GitHub token UI and repository policy.

## Safety and limitations

- Issue creation requires both a token and the `--confirm-public-write` flag.
- The API client only contacts `api.github.com` and supports only GET and POST.
- HTTP errors are reported without dumping response bodies or credentials.
- Requests have a timeout and response-size limit.
- The client does not implement OAuth, token refresh, a GitHub App, webhook handling, or multi-user authorization.
- For a public multi-user service, each user needs their own consent and authorization flow. Do not use a single developer's token for all users.

## Manual verification

Start with read-only access:

```bash
devna github repo octocat/Hello-World
devna github issues octocat/Hello-World --limit 5
```

Do not test issue creation against a real project without permission. Use a dedicated sandbox repository and a token scoped only to that repository.
