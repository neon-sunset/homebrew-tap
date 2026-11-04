# Dotheap Homebrew tap

On Apple silicon running macOS 15 or later:

```sh
brew install --cask neon-sunset/tap/dotheap
```

Homebrew installs the precompiled CLI on your PATH and puts `Dotheap.app` in
`/Applications`. No Rust or Xcode installation is required. The fully qualified
install command also grants Homebrew trust for this cask.

The cask removes quarantine only from Dotheap's app and CLI so both can run
immediately. It preserves their ad-hoc signatures and debugger entitlements.
The binaries are not notarized by Apple. Capturing a live process still requires
macOS debugger access; opening an existing dump does not require debugger access.

To update both:

```sh
brew upgrade --cask dotheap
```

To replace a source installation at the same version:

```sh
brew reinstall --cask dotheap
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
version and combined archive's SHA-256. `livecheck` detects the latest published
release; it does not update this repository automatically.

```sh
brew bump-cask-pr --write-only --version X.Y.Z neon-sunset/tap/dotheap
brew style Casks/dotheap.rb
python3 tests/check-dotheap.py /path/to/dotheap-macos-arm64-bundle.tar.gz
```

The test uses temporary cask, app, and CLI names. It checks download checksums,
signatures, debugger entitlements, quarantine removal, CLI launch, upgrades from
the source cask layout, reinstalls, custom app directories, and removal. Add
`--launch` in a desktop session to check that the Viewer opens without approval.
It leaves an existing Dotheap installation in place.

See [macOS distribution](https://github.com/neon-sunset/dotheap/blob/main/docs/macos-distribution.md)
for packaging, release checks, and Gatekeeper behavior.
