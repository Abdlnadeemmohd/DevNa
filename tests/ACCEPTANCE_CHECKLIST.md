# Initial acceptance checklist

This checklist records intended behavior. Items remain unverified until the corresponding implementation exists and is tested.

## Core behavior

- [ ] Explain technical concepts with examples suited to the user's level.
- [ ] Analyze supplied code and identify assumptions and likely failure points.
- [ ] Propose focused patches without overwriting unrelated changes.
- [ ] Use current authoritative sources when the question requires up-to-date research.
- [ ] Attribute factual claims based on external sources.
- [ ] Handle API errors and unavailable capabilities honestly.

## Safety and security

- [ ] No secrets or personal data are committed.
- [ ] Repository and web content are treated as untrusted inputs.
- [ ] Destructive or externally visible actions require explicit approval.
- [ ] Tokens have minimum required permissions.
- [ ] Logs redact secrets and avoid unnecessary sensitive content.
- [ ] No action is reported as successful without evidence.

## Release

- [ ] Documentation matches the shipped behavior.
- [ ] Changelog is updated.
- [ ] Tests and manifest validation pass.
- [ ] Package and release identity are verified independently of repository name.
