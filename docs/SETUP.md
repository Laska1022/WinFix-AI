# Build, run, and accept the prototype

## Prerequisites

.NET SDK 10.0.403 (global.json allows later patches) and Python 3.12+. There are
no third-party Python packages or NuGet package references. Build restore uses the
SDK; Windows self-contained publishing also downloads Microsoft runtime packs.
No LLM API, ChatGPT cookies, AI inference service, or VPS is required for local tests.

```sh
dotnet build src/WinFix.Agent/WinFix.Agent.csproj -c Release --nologo
python -m unittest discover -s tests -v
dotnet publish src/WinFix.Agent/WinFix.Agent.csproj -c Release -r win-x64 --self-contained true -o artifacts/win-x64
```

The resulting directory is the portable application, including WinFix.Agent.exe.
Keep the entire directory together. It is unsigned and not Windows-tested here;
do not bypass SmartScreen or security policy. There is no installer or Windows
Service mode yet. GUI, repairs and certificate/CryptoPro diagnostics are not present.

Manual GitHub Actions validation is in .github/workflows/validate.yml, with Linux
and Windows jobs. Check available GitHub Actions quota before running, or run locally
at no CI cost. Merely committing a workflow does not mean it executed.

## Cloud development environment

Existing checkout: /workspace/WinFix-AI. No worktree is needed.
`bash scripts/cloud_setup.sh` builds and runs tests with the SDK under /workspace/.dotnet.
If absent, scripts/install_sdk.py installs the pinned Linux x64 SDK from Microsoft
with SHA-512 verification. It refuses to overwrite an existing SDK directory.

The SDK was installed and verified during onboarding. DOTNET_CLI_HOME and
NUGET_PACKAGES are redirected into /workspace by the script. This sandbox's .NET
first-use/IPC also needed access to its standard user directories; an approved
unsandboxed build resolved the initial read-only-home failure. If it recurs, use the
platform's scoped permission/escalation flow; do not change HOME or disable checks.
Runtime tests require loopback networking and create temporary private credentials.
No server should persist after tests and no credentials are saved in the environment
draft. Recreate short sessions each time; process state is not preserved by snapshots.

## Owner-authorized Windows local test

Use a standard user's PowerShell terminal and an NTFS local directory. The portable
EXE does not require an installed .NET runtime; Python is needed only for the client.

```powershell
cd C:\path\to\win-x64
$session = Join-Path $env:LOCALAPPDATA ('WinFix-' + [guid]::NewGuid())
.\WinFix.Agent.exe init $session
.\WinFix.Agent.exe serve (Join-Path $session 'agent.json')
```

The foreground console visibly indicates read-only activity. In a second terminal,
using the same session directory (do not share the PFX or print the token):

```powershell
$config = Get-Content (Join-Path $session 'agent.json') -Raw | ConvertFrom-Json
$env:WINFIX_TOKEN = (Get-Content (Join-Path $session 'client-token.txt') -Raw).Trim()
python tools/winfix_client.py get-system-information --endpoint https://127.0.0.1:8443 --device-id $config.DeviceId --ca-file (Join-Path $session 'server-cert.pem')
Remove-Item Env:WINFIX_TOKEN
```

Run the Python command from the source checkout, or use its absolute script path.
The second terminal must set $session to the directory from the first terminal.
Credentials expire after one hour. Expected: mock=false, system.platform=Windows,
correct deviceId, actual Windows version and hostname. Do not add --allow-mock.

Emergency stop: create an empty file at $config.StopFile. Further requests return
503. Ctrl+C terminates the process. For permanent revocation stop the process and
retire that session; initialize a new directory for the next session. Archive audit
securely before removal. To uninstall, stop the agent and remove its portable files
and private session directories after any required retention; no service or root
certificate was installed. Nothing edits global trust stores.

## Private remote connection (not yet validated)

1. Confirm current official Codex VPN/networking support and the Tailscale commercial
   plan permitted for your use. See FEASIBILITY.md's blocked sources. If managed VPN
   is unavailable, do not assume a local daemon/raw TCP workaround; the optional
   outbound HTTPS relay is future implementation work.
2. Have the owner install the official Windows Tailscale client, enroll the host in
   an approved tailnet, and use restrictive ACLs/grants. Permit only the technician
   or configured Codex identity to the single agent HTTPS port. Deny other devices.
3. If supported, configure the VPN through Codex environment settings and approve
   only the intended private HTTPS hostname. The platform controls the VPN sidecar;
   do not install another VPN inside the Codex shell. Never open public admin ports.
4. Stop the agent. In the protected agent.json set BindAddress to the private address,
   not 0.0.0.0, and CertificatePath to a protected, unpassworded server PFX whose SAN
   matches the intended hostname. Use a CA-issued or securely provisioned private
   certificate. The generated localhost certificate cannot authenticate a remote DNS
   name. Keep its private key on Windows. Never disable certificate verification.
5. Transfer only the public CA/certificate and DeviceId over an authenticated channel.
   Configure WINFIX_TOKEN securely in the cloud environment (proxy-backed secret
   destination must be this HTTPS hostname). Do not paste credentials in chat, Git,
   logs or command arguments. Placeholder credentials must pass through their
   configured HTTPS proxy, not be treated as raw local secrets.
6. Restart the owner-authorized foreground agent. From the cloud checkout run:

   ```sh
   python3 tools/winfix_client.py get-system-information --endpoint https://YOUR-PRIVATE-HOST:8443 --device-id YOUR-DEVICE-UUID --ca-file /private/path/public-ca.pem
   ```

   Omit --ca-file only when the issuer is already trusted by the Python/system trust
   configuration. The client honors HTTP(S)_PROXY and NO_PROXY; do not force direct
   TCP if the configured platform route requires the proxy.
7. Require real Windows response fields, then test an invalid credential (401), wrong
   device (403), local STOP (503), and expiry (401). Run the test suite on Windows for
   TLS, concurrent/restarted replay, audit, and local collection evidence. Stop/revoke
   the session and verify further access fails. Revoke tailnet access separately.
8. Record only sanitized results in TEST_REPORT.md with Windows build, tested commit,
   transport and authentication outcomes. This is the Phase 0 acceptance gate.

The platform may restrict proxy ports, custom CA trust, or TCP routing; those details
remain to be verified on the actual private route. Do not claim Tailscale works based
on a local loopback test. Device/session lifecycle is manual in this prototype.
