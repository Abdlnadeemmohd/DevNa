# DevNa Privacy Policy

**Draft for publisher review.** Before submitting, review this policy against the actual hosting provider, search providers, deployment settings, and any monitoring configured for the service.

## What DevNa processes

DevNa processes the information necessary to answer tool requests, including:
- Search queries submitted to the web-search tool.
- Public GitHub repository names and file paths.
- Text, source snippets, JSON, and logs that a user submits for static analysis.
- API host/path parameters for allowlisted read-only JSON requests.
- Automation task descriptions submitted for planning.

Do not submit passwords, access tokens, private keys, production secrets, customer records, or other sensitive data. The service refuses some sensitive filename patterns, but users remain responsible for the content they provide.

## How information is used

The service uses tool inputs to make the requested search or public API read, or to perform static analysis in memory. The application code is designed not to persist tool input or output and does not intentionally log submitted source content. Hosting providers may retain operational logs and metadata under their own retention and security policies.

Web-search queries are passed to the search backend used by the `ddgs` library and may be processed under that provider's policies. Public GitHub requests go to GitHub's API. Allowlisted API calls go to the configured public HTTPS host.

## Credentials

The public MCP server does not ask users to provide tokens and does not accept user-supplied authorization headers. It does not access private GitHub repositories or perform remote write operations.

## Retention and security

DevNa does not intentionally store tool inputs in an application database. The deployment operator and hosting provider may process connection metadata and service logs. No public internet service can promise zero risk, and users should avoid sending sensitive content.

## Children and contact

DevNa is a general-purpose developer tool and is not intended to collect data from children. For support or privacy questions, use the repository's issue page: https://github.com/Abdlnadeemmohd/DevNa/issues. Do not include private or sensitive data in public issues.

## Changes

This policy may be updated to reflect the final deployment and operational practices. The publisher should update this page before launch if actual data handling differs from this description.
