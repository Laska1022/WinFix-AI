# WinFix AI Windows x64 preview

Includes all three reviewed bug fixes. Unsigned preview; Windows execution and
installation have not been validated. This is a command-line diagnostics agent,
not the separate interactive installer. Do not bypass Windows security controls.

WinFix.Agent.exe is a self-contained single-file build. It includes the .NET
runtime and native libraries (extracted at runtime); no separate .NET install is
required. The ZIP also contains the Python client, setup/security instructions,
and license. Python 3.12+ is needed only for the client.

In a standard-user PowerShell terminal, from the extracted directory:

```powershell
$session = Join-Path $env:LOCALAPPDATA ('WinFix-' + [guid]::NewGuid())
.\WinFix.Agent.exe init $session
.\WinFix.Agent.exe serve (Join-Path $session 'agent.json')
```

Keep the session directory private. Follow docs/SETUP.md for the client request,
local stop, credential expiry and private connection requirements. Do not upload
session tokens or private certificates. This build does not prove Windows or
private-network acceptance. See SHA256SUMS.txt for artifact checksums.

Source commit: adcf3aef88ec1ce6d9374c8ffc95f869978955c9

## Download files

- [Windows x64 EXE](https://github.com/Laska1022/WinFix-AI/raw/refs/heads/release/windows-bugfix-preview-20261105/downloads/bugfix-preview-20261105/WinFix.Agent.exe)
- [Portable ZIP with client and documentation](https://github.com/Laska1022/WinFix-AI/raw/refs/heads/release/windows-bugfix-preview-20261105/downloads/bugfix-preview-20261105/WinFix-AI-win-x64-portable.zip)
- [SHA-256 checksums](SHA256SUMS.txt)

These are repository-hosted downloads. A GitHub Release has not been created:
the current cloud runtime denies the GitHub release API despite the saved domain
allowlist draft. The EXE is the command-line agent, not the separate installer.
