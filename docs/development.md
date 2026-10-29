# Development workflow

## Requirements

Python 3.11 or later. Runtime code currently uses only the standard library.

## Local setup

```bash
python -m venv .venv
# Activate the environment:
python -m pip install -e .
```

## Verify changes

From the repository root:

```bash
# Inspect the plan only
devna automate verify --root .

# Execute the fixed checks
devna automate verify --root . --execute

# Or run tests directly
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

The verification command uses a fixed list of subprocess argument arrays, `shell=False`, and bounded timeouts. It does not accept arbitrary commands. The default mode is dry-run.

## GitHub credentials

Public repository metadata and public issues can be read without a token, subject to API rate limits. Set `GITHUB_TOKEN` or `GH_TOKEN` when you need access to private repositories or write an issue. Do not print token values or commit them to files.

Use a fine-grained token for a local experiment and scope it to the specific repository and permissions required. For multi-user public products, implement a GitHub App or OAuth-based authorization rather than sharing a personal token.

## Contribution flow

1. Create a feature branch.
2. Make focused changes.
3. Run the checks and inspect the complete diff.
4. Open a pull request with the test results and risks.
5. Do not merge or release until the review and required checks succeed.

The existing ChatGPT plugin release is managed separately from GitHub source commits. See [plugin identity](plugin-identity.md).
