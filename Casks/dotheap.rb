cask "dotheap" do
  version "0.2.2"
  sha256 "464213aa7bbef0d2b62c5976b7c236028c386c7cd2d9f809f9bd49177d6dd38c"

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
