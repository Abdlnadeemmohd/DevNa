# DevNa Privacy Policy

**Effective date:** October 29, 2026.

DevNa provides public web search, public GitHub repository inspection, static analysis of user-submitted text, read-only JSON requests to a configured allowlist of public HTTPS APIs, and automation planning.

## Information processed

When you use DevNa, the service may process:
- Your search queries.
- Public GitHub owner/repository names, issue requests, and requested public file paths.
- Text, code, JSON, CSV/TSV content, and logs you provide for static analysis.
- An API hostname and relative path for an allowlisted public JSON request.
- A task description you submit for an automation plan.
- Basic connection information processed by the hosting platform, such as request metadata, timing, and operational logs.

Do not provide passwords, access tokens, private keys, confidential source code, production secrets, customer records, health data, or other sensitive information. The tool has filename and size safeguards, but those safeguards are not a substitute for your judgment.

## How the service uses information

The server uses the request content to provide the selected tool result. The application code has no user-content database and does not intentionally write tool inputs or outputs to persistent storage. Transient processing happens in memory. The hosting platform may process connection metadata and operational logs according to its own policy and configuration.

The web-search tool sends the query to the search backend used by the `ddgs` library. Public GitHub lookups are sent to GitHub's public API. Requests to other services are limited to the public HTTPS hosts explicitly allowlisted by the service operator.

## What the service does not do

The public version does not accept user-supplied API credentials, access private GitHub repositories, create or edit GitHub content, write to external APIs, execute submitted code, execute shell commands, or schedule background tasks.

## Third-party services

GitHub, the web-search backend, the hosting provider, and any configured allowlisted API host are third-party services. Their operators may process requests under their own privacy policies and terms. DevNa does not control their retention, availability, or independent handling of data. Search results and API responses may be incomplete or inaccurate.

## Retention and security

DevNa's application code does not maintain a persistent store of user tool content. Hosting infrastructure and upstream providers may retain operational records under their own policies. No public internet service can guarantee zero risk. Avoid sending sensitive material and use only public sample data where possible.

## Children

DevNa is a general-purpose developer tool and is not designed for children.

## Contact

For questions or concerns, use the support page at https://github.com/Abdlnadeemmohd/DevNa/issues. Do not include passwords, tokens, private keys, or other sensitive information in a public issue.

## Changes

This policy may be updated when data flows, features, or hosting arrangements change. The published version should accurately reflect the actual configuration and behavior of the deployed service.
