cask "dotheap" do
  version "0.2.7"
  sha256 "f4faf4ecc45538b03402192a0eddfeaf866a58e33d1e7983b0ad53362c2ae2ea"

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
