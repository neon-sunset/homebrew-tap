#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid


def run(*args, check=True):
    result = subprocess.run(args, text=True, capture_output=True, env=environment, stdin=subprocess.DEVNULL)
    if check and result.returncode:
        sys.exit(result.stdout + result.stderr)
    return result


def brew(*args, check=True):
    print("brew " + " ".join(map(str, args)), flush=True)
    result = run(brew_path, *map(str, args), check=check)
    print(result.stdout + result.stderr, end="", flush=True)
    return result


environment = os.environ | {"HOMEBREW_NO_AUTO_UPDATE": "1", "HOMEBREW_NO_ANALYTICS": "1",
                            "HOMEBREW_NO_AUTOREMOVE": "1", "HOMEBREW_NO_INSTALL_CLEANUP": "1"}
brew_path = shutil.which("brew")
if not brew_path or len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--launch"):
    sys.exit(f"Usage: {sys.argv[0]} MACOS_BUNDLE_ARCHIVE [--launch] (requires Homebrew on Apple silicon)")
archive = Path(sys.argv[1]).resolve()
source = (Path(__file__).resolve().parents[1] / "Casks/dotheap.rb").read_text()
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
assert re.search(r'sha256 "([a-f0-9]+)"', source)[1] == checksum
version = re.search(r'version "([^"]+)"', source)[1]
prefix = Path(run(brew_path, "--prefix").stdout.strip())
repository = Path(run(brew_path, "--repository").stdout.strip())
token = "dotheap-test-" + uuid.uuid4().hex[:8]
tap = repository / "Library/Taps/dotheap-test" / ("homebrew-" + token)
qualified = "dotheap-test/" + token + "/" + token
binary = prefix / "bin" / token
app_name = "Dotheap Test " + token + ".app"
default_app = Path("/Applications") / app_name
assert not binary.exists() and not default_app.exists() and not tap.exists()

with tempfile.TemporaryDirectory(prefix="dotheap-cask-") as directory:
    temporary = Path(directory)
    environment["HOMEBREW_CACHE"] = str(temporary / "cache")
    environment["XDG_CONFIG_HOME"] = str(temporary / "config")
    with tarfile.open(archive) as package:
        cli_hash = hashlib.sha256(package.extractfile("dotheap").read()).hexdigest()
        gui_hash = hashlib.sha256(package.extractfile("Dotheap.app/Contents/MacOS/DotheapViewer").read()).hexdigest()
        old_archive = temporary / "source-layout.tar.gz"
        with tarfile.open(old_archive, "w:gz") as old:
            for member in package.getmembers():
                stream = package.extractfile(member) if member.isfile() else None
                member.name = "dotheap-0.0.0/" + ("bin/dotheap" if member.name == "dotheap" else member.name)
                old.addfile(member, stream)
    fixture = source.replace('cask "dotheap"', f'cask "{token}"')
    fixture = re.sub(r'^  url ".*"$', f'  url "{archive.as_uri()}"', fixture, flags=re.M)
    fixture = fixture.replace('app "Dotheap.app"', f'app "Dotheap.app", target: "{app_name}"')
    fixture = fixture.replace('binary "dotheap"', f'binary "dotheap", target: "{token}"')
    fixture = fixture.replace("{{appdir}}/Dotheap.app", "{{appdir}}/" + app_name)
    old_fixture = fixture.replace(f'version "{version}"', 'version "0.0.0"')
    old_fixture = old_fixture.replace(archive.as_uri(), old_archive.as_uri())
    old_fixture = old_fixture.replace(checksum, hashlib.sha256(old_archive.read_bytes()).hexdigest())
    old_fixture = old_fixture.replace('app "Dotheap.app"', 'app "dotheap-0.0.0/Dotheap.app"')
    old_fixture = old_fixture.replace('binary "dotheap"', 'binary "dotheap-0.0.0/bin/dotheap"')
    old_fixture = re.sub(r"  postflight_steps do\n.*?^  end\n", "", old_fixture, flags=re.M | re.S)
    fixture = fixture.replace('  postflight_steps do', """  preflight_steps do
    run "/usr/bin/xattr", args: ["-p", "com.apple.quarantine", "{{staged_path}}/Dotheap.app"]
    run "/usr/bin/xattr", args: ["-p", "com.apple.quarantine", "{{staged_path}}/dotheap"]
  end

  postflight_steps do""")
    cask_file = tap / "Casks" / (token + ".rb")
    cask_file.parent.mkdir(parents=True)
    run("git", "init", "--quiet", str(tap))

    def verify(app, quarantined=False):
        assert app.is_dir() and binary.is_symlink()
        assert hashlib.sha256(binary.read_bytes()).hexdigest() == cli_hash
        assert hashlib.sha256((app / "Contents/MacOS/DotheapViewer").read_bytes()).hexdigest() == gui_hash
        for path in (app, binary.resolve()):
            run("codesign", "--verify", "--deep", "--strict", str(path))
            attributes = run("/usr/bin/xattr", "-r", str(path)).stdout
            assert ("com.apple.quarantine" in attributes) == quarantined, attributes
            entitlements = run("codesign", "--display", "--entitlements", "-", "--xml", str(path)).stdout
            assert "com.apple.security.cs.debugger" in entitlements
        if not quarantined:
            assert run(str(binary), "--version").stdout.strip() == version
            run(str(binary), "help")
        data = json.loads(run(brew_path, "info", "--json=v2", "--cask", qualified).stdout)["casks"][0]
        assert not data["depends_on"].get("formula") and not data["depends_on"].get("cask"), data["depends_on"]

    def launch(app):
        script = """ObjC.import('AppKit');
function run(argv) {
  const apps = $.NSWorkspace.sharedWorkspace.runningApplications;
  for (let i = 0; i < apps.count; i++) {
    const app = apps.objectAtIndex(i);
    if (ObjC.unwrap(app.bundleURL.path) === argv[0] && app.finishedLaunching) {
      return Number(app.processIdentifier);
    }
  }
  return 0;
}"""
        app = app.resolve()
        run("/usr/bin/open", "-g", "-j", "-n", str(app), "--args", "-ApplePersistenceIgnoreState", "YES")
        pid = 0
        try:
            for _ in range(30):
                pid = int(run("/usr/bin/osascript", "-l", "JavaScript", "-e", script, str(app)).stdout.strip())
                if pid:
                    break
                time.sleep(0.5)
            assert pid, f"Viewer did not finish launching: {app}"
            os.kill(pid, 0)
            print("Viewer launched through Launch Services without approval.", flush=True)
        finally:
            if pid:
                os.kill(pid, signal.SIGTERM)

    try:
        cask_file.write_text(fixture.replace(checksum, "0" * 64))
        result = brew("install", "--cask", qualified, check=False)
        assert result.returncode and "checksum" in (result.stdout + result.stderr).lower()
        cask_file.write_text(old_fixture)
        brew("install", "--cask", qualified)
        assert "dotheap-0.0.0/bin/dotheap" in str(binary.resolve())
        verify(default_app, quarantined=True)
        cask_file.write_text(fixture)
        brew("upgrade", "--cask", qualified)
        verify(default_app)
        assert binary.resolve() == prefix / "Caskroom" / token / version / "dotheap"
        assert not (prefix / "Caskroom" / token / "0.0.0").exists()
        brew("reinstall", "--cask", qualified)
        verify(default_app)
        brew("uninstall", "--cask", qualified)
        assert not binary.is_symlink() and not default_app.exists()
        custom = temporary / "Applications with spaces"
        brew("untrust", "--cask", qualified)
        brew("install", "--cask", "--appdir=" + str(custom), qualified)
        verify(custom / app_name)
        if "--launch" in sys.argv:
            launch(custom / app_name)
        cask_file.write_text(source.replace('cask "dotheap"', f'cask "{token}"'))
        brew("livecheck", "--cask", "--json", qualified)
        cask_file.write_text(fixture)
        brew("uninstall", "--cask", qualified)
        assert not binary.is_symlink() and not (custom / app_name).exists()
        assert not (prefix / "Caskroom" / token).exists()
        print("Verified one-command install, quarantine removal, CLI launch, checksums, upgrade, reinstall and uninstall.")
    finally:
        if (prefix / "Caskroom" / token).exists():
            brew("uninstall", "--cask", "--force", qualified, check=False)
        shutil.rmtree(tap)
