# Plugin identity and release workflow

## Current source baseline

The existing ChatGPT plugin is named `devna`, is at version `1.0.1`, and has private discoverability. Its backend identity is managed by the plugin platform, not by this Git repository.

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
