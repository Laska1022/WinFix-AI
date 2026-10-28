"""Install the pinned Linux x64 SDK from Microsoft, verifying SHA-512 before extraction."""
import hashlib
import json
from pathlib import Path
import platform
import tarfile
import tempfile
import urllib.request

if platform.system() != "Linux" or platform.machine() != "x86_64":
    raise SystemExit("This cloud bootstrap targets Linux x64; install the pinned SDK from Microsoft on other platforms.")
version = json.loads((Path(__file__).resolve().parents[1] / "global.json").read_text())["sdk"]["version"]
with urllib.request.urlopen("https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json", timeout=30) as response:
    releases = json.load(response)
artifact = next(f for r in releases["releases"] for s in r.get("sdks", []) if s["version"] == version
                for f in s["files"] if f["rid"] == "linux-x64")
if not artifact["url"].startswith("https://builds.dotnet.microsoft.com/dotnet/"):
    raise SystemExit("Unexpected SDK origin")
target = Path("/workspace/.dotnet")
if target.exists():
    raise SystemExit("SDK directory already exists; inspect it before replacing an existing installation")
with tempfile.TemporaryDirectory() as directory:
    archive = Path(directory) / "sdk.tar.gz"
    digest = hashlib.sha512()
    with urllib.request.urlopen(artifact["url"], timeout=60) as response, archive.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
    if digest.hexdigest().lower() != artifact["hash"].lower():
        raise SystemExit("SDK SHA-512 verification failed")
    with tarfile.open(archive) as package:
        package.extractall(target, filter="data")
print(f"Installed verified .NET SDK {version}")
