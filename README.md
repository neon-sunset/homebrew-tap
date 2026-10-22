# Dotheap Homebrew tap

On macOS 15 or later, install Xcode 16 or later, then run:

```sh
brew install --cask neon-sunset/tap/dotheap
```

Homebrew installs Rust, builds the tagged Dotheap release from source, installs the CLI on your PATH,
and puts `Dotheap.app` in `/Applications`.

To update both:

```sh
brew upgrade --cask dotheap
```

To remove the CLI and Viewer:

```sh
brew uninstall --cask dotheap
```

Dump files and analysis caches are retained. Manage caches in the Viewer's **File > Cache** menu.
