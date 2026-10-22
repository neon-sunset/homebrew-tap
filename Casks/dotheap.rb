cask "dotheap" do
  version "0.1.0"
  sha256 "5d290e9d1848cf72e4becc4e588e9b41513ecd0ad0217199f1d2f39247f2c6c3"

  url "https://github.com/neon-sunset/dotheap/releases/download/v#{version}/dotheap-source.tar.gz"
  name "Dotheap"
  desc "Managed and native memory analysis for .NET dumps"
  homepage "https://github.com/neon-sunset/dotheap"

  depends_on formula: "rust"
  depends_on macos: :sequoia

  installer script: {
    executable: "#{staged_path}/dotheap-#{version}/scripts/build-macos.sh",
  }

  app "dotheap-#{version}/Dotheap.app"
  binary "dotheap-#{version}/bin/dotheap"

  postflight_steps do
    remove "dotheap-#{version}/.build", recursive: true
    remove "dotheap-#{version}/target", recursive: true
  end

  caveats <<~EOS
    Dotheap builds from source. Xcode 16 or later must be installed and selected with xcode-select.
  EOS
end
