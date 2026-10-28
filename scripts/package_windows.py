"""Build a self-contained Windows EXE and an NSIS per-user installer."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.2-preview"
output = ROOT / "artifacts" / VERSION
publish = output / "publish"
output.mkdir(parents=True, exist_ok=True)
dotnet = os.environ.get("DOTNET", "dotnet")
makensis = os.environ.get("MAKENSIS", "makensis")
subprocess.run([dotnet, "publish", str(ROOT / "src/WinFix.Agent/WinFix.Agent.csproj"),
                "-c", "Release", "-r", "win-x64", "--self-contained", "true", "-o", str(publish),
                "-p:PublishSingleFile=true", "-p:IncludeNativeLibrariesForSelfExtract=true",
                "-p:EnableCompressionInSingleFile=true", "-p:DebugType=None", "-p:DebugSymbols=false"],
               cwd=ROOT, check=True)
app = publish / "WinFix.Agent.exe"
installer = output / f"WinFixAI-Setup-{VERSION}.exe"
prefix = "/" if os.name == "nt" else "-"
subprocess.run([makensis, f"{prefix}DAPP_FILE={app}", f"{prefix}DOUTPUT_FILE={installer}",
                str(ROOT / "packaging/WinFixAI.nsi")], cwd=ROOT / "packaging", check=True)
manifest = {"version": VERSION, "sourceCommit": subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "sourceDirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
    "windowsExecutionTested": False, "files": {}}
for path in (app, installer):
    if path.read_bytes()[:2] != b"MZ":
        raise SystemExit(f"Not a PE executable: {path.name}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest["files"][path.name] = {"size": path.stat().st_size, "sha256": digest}
(output / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
(output / "SHA256SUMS.txt").write_text("".join(f"{v['sha256']}  {k}\n" for k, v in manifest["files"].items()))
print(f"Built unsigned Windows preview in {output}")
