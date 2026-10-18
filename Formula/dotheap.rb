class Dotheap < Formula
  desc "Memory analyzer for .NET process dumps: managed heap (Satori and CoreCLR GC) and native memory"
  homepage "https://github.com/neon-sunset/dotheap"
  head "https://github.com/neon-sunset/dotheap.git", branch: "main"

  on_macos do
    depends_on xcode: ["16.0", :build]
    depends_on "rust" => :build
  end

  def install
    if OS.mac?
      system "cargo", "build", "--locked", "--release", "-p", "dotheap"
      bin.install "target/release/dotheap"
      doc.install "THIRD-PARTY-NOTICES.txt"
      system "scripts/make-app.sh", "--disable-sandbox"
      prefix.install "Dotheap.app"
    else
      odie "On Linux, install the static binary from the GitHub release"
    end
  end

  def caveats
    on_macos do
      <<~EOS
        The viewer app is in #{opt_prefix}/Dotheap.app. To add it to Applications:
          ln -sf #{opt_prefix}/Dotheap.app /Applications/Dotheap.app
      EOS
    end
  end

  test do
    assert_match "usage: dotheap", shell_output("#{bin}/dotheap help")
  end
end
