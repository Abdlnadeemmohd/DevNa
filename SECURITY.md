# Security Policy

## Reporting a vulnerability

Do not publish credentials, exploit details, or sensitive personal information in a public issue. Use GitHub's private vulnerability reporting feature for this repository if enabled. Otherwise, contact the repository owner privately through a channel listed on their GitHub profile.

## Security expectations

- Never commit secrets, credentials, private keys, or production data.
- Use least-privilege permissions for tokens and integrations.
- Treat local files, external content, and API responses as untrusted input.
- Ask for explicit confirmation before destructive or externally visible actions.
- The CLI's issue-creation command requires a configured token and explicit confirmation.
- The automation planner defaults to dry-run and uses fixed commands rather than arbitrary shell strings.
- Logs and command output must not disclose token values or unnecessary sensitive content.

## Known limitations

DevNa Core is an alpha local CLI, not a hardened hosted service. It does not currently provide multi-user authentication, a hosted API, scheduled background execution, or production-grade audit logging. Do not use it as a security boundary for untrusted multi-tenant workloads.
