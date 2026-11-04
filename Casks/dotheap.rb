cask "dotheap" do
  version "0.2.6"
  sha256 "a50e3fcd5981d2891c1ee48690cb5b0396e0a5983d4e7234bc9be2cab75899ec"

  url "https://github.com/neon-sunset/dotheap/releases/download/v#{version}/dotheap-macos-arm64-bundle.tar.gz"
  name "Dotheap"
  desc "Managed and native memory analysis for .NET dumps"
  homepage "https://github.com/neon-sunset/dotheap"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on arch: :arm64
  depends_on macos: :sequoia

  app "Dotheap.app"
  binary "dotheap"

  postflight_steps do
    on_macos do
      run "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "{{appdir}}/Dotheap.app"]
      run "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "{{staged_path}}/dotheap"]
    end
  end
end
