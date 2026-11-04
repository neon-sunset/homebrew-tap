# Dotheap Homebrew tap

On Apple silicon running macOS 15 or later:

```sh
brew install --cask neon-sunset/tap/dotheap
```

Homebrew installs the precompiled CLI on your PATH and puts `Dotheap.app` in
`/Applications`. The cask removes quarantine from Dotheap's ad-hoc-signed binaries
so both can run immediately. Live process capture requires macOS debugger access.

To update both:

```sh
brew upgrade --cask dotheap
```

To remove the CLI and Viewer:

```sh
brew uninstall --cask dotheap
```

Dump files, preferences, and analysis caches are retained. Manage caches in the
Viewer's **File > Cache** menu.

## Updating the cask

Publish `dotheap-macos-arm64-bundle.tar.gz` and its `SHA256SUMS` entry in the Dotheap
release before changing the cask. Set `version` and `sha256` to the published
version and combined archive's SHA-256. `livecheck` reports the latest published
release.

```sh
brew bump-cask-pr --write-only --version X.Y.Z neon-sunset/tap/dotheap
brew style Casks/dotheap.rb
python3 tests/check-dotheap.py /path/to/dotheap-macos-arm64-bundle.tar.gz
```

The test checks checksums, signatures, debugger entitlements, quarantine removal,
CLI launch, installation, upgrades, reinstalls, and removal. It uses temporary
cask, app, and CLI names. Add `--launch` in a desktop session to check Viewer launch.

See [macOS distribution](https://github.com/neon-sunset/dotheap/blob/main/docs/macos-distribution.md)
for packaging, release checks, and Gatekeeper behavior.
