cask "dotheap" do
  version "0.2.5"
  sha256 "0e4ce919addff863a41e3cecfa5b0243ea1382436554ff62fabf726f098a2699"

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
