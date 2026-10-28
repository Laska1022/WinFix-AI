# Phase 0 feasibility evidence

Recorded 2026-10-28. The starting GitHub repository advertised no refs or commits.
No previous project implementation, documentation, or results could be recovered.

## Observed here

- Debian/Linux x64 cloud shell, Python 3.12.14, initially no .NET SDK.
- .NET SDK 10.0.403 / runtime 10.0.14 installed from Microsoft over verified TLS;
  official Linux SDK archive SHA-512 checked against release metadata.
- GitHub HTTPS Git access works through the supplied proxy.
- HTTPS_PROXY/HTTP_PROXY and related proxy settings are present; values not logged.
  No WINFIX or TAILSCALE variable names were present. A proxy does not prove VPN access.
- Actual loopback HTTPS agent/client integration and failure tests run successfully.
- The user confirmed there is no Windows test computer available yet.
- The cloud onboarding platform instructions describe managed VPN in an egress
  proxy sidecar. They do not establish that a Tailscale connection is configured,
  licensed for this use, or reachable in this particular environment.

## Official documentation review: blocked, not completed

Requests to these intended official sources returned proxy tunnel 403:

- https://developers.openai.com/codex/cloud/internet-access
- https://developers.openai.com/codex/cloud/environments
- https://tailscale.com/kb/1586/codex (candidate documentation URL; existence unverified)
- https://tailscale.com/pricing

The environment draft adds developers.openai.com and tailscale.com to the custom
allowlist while preserving package-manager presets. A saved draft is not an applied
network policy or publication. Review/save settings, publish when appropriate, then
retry and locate the current official Codex integration page through Tailscale's KB.
Do not quote provider plan limits or assert native Tailscale availability until read.
Do not install a second VPN client inside the Codex machine.

Microsoft sources accessed successfully:

- https://dot.net/v1/dotnet-install.sh
- https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json

## Deployment comparison

| Option | Advantages | Prerequisites / current evidence |
| --- | --- | --- |
| Platform-managed Tailscale/private HTTPS | No VPS, private device ACLs; application auth remains independent | Requires supported Codex VPN configuration, private HTTPS routing, verified certificate and current commercial licensing review. Not tested here. |
| Privately controlled VPS relay | Outbound HTTPS from Windows, multiple devices, independent hosting geography | Requires hosting/TLS/identity/queue/replay security and operating cost. Not implemented. No public RDP/SMB/WinRM or arbitrary PowerShell endpoint. |
| Local HTTPS | No hosting cost; repeatable protocol tests | Implemented on loopback. Does not establish remote reachability. |

Selected first milestone: transport-independent HTTPS read-only protocol with local
tests, followed by one real private Windows HTTPS acceptance. This is the smallest
verifiable prerequisite for either deployment. Do not add a VPS prematurely.

## Gate to Phase 1

Run SETUP.md's acceptance from a fresh Codex task against an owner-authorized
Windows host. Require verified TLS, correct identity, non-mock Windows diagnostics,
negative authentication, stop/revocation, and restart replay checks. Record sanitized
results, Windows build, proxy/VPN route, certificate trust setup, and exact commit.
Linux tests and a cross-compiled EXE do not satisfy this gate.
