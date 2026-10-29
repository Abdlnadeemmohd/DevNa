# Plugin identity and release workflow

## Current source baseline

The existing ChatGPT plugin is named `devna`, is at version `1.0.2`, and has private discoverability. Version 1.0.2 was verified after updating the existing plugin in place. Its backend identity is managed by the plugin platform, not by this Git repository.

The source manifests in this repository describe the package name and version. They do **not** create a new plugin identity.

## Updating the existing plugin

1. Make and review the intended source changes in this repository.
2. Validate the package files and test the behavior.
3. Package the manifest and `skills/` files using the supported plugin packaging workflow.
4. Use the plugin platform's **update existing plugin** action with the existing plugin's exact backend ID and current release as the guard.
5. Verify the resulting version and confirm the existing plugin remains private.

Do not use a create-new-plugin workflow for an update. Do not treat a Git commit, repository name, or package version as proof that a release was uploaded or published.

## Public-repository precautions

This repository is public. Do not commit personal email addresses, credentials, private release archives, or the plugin platform's backend ID. Keep that ID in the plugin platform or another private record. The public repository can contain source files while the ChatGPT plugin itself remains private.


## Public listing architecture

The current plugin remains a private, skills-only plugin at version 1.0.2. OpenAI's current public-submission documentation says an MCP server cannot be added later to an existing skills-only plugin. The full public MCP version is therefore prepared as a separate initial submission package at `public-plugin/`, with a new package identifier `devna-public-copilot` and the same user-facing display name, DevNa.

This does not delete, rename, or expose the existing private plugin. The public package is not an OpenAI listing until you upload it, connect the deployed endpoint, complete publisher verification and review, and choose Publish after approval.
