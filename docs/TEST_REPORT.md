# Test report

Environment: Linux x64 cloud instance, Python 3.12.14, .NET SDK 10.0.403 /
runtime 10.0.14. Date: 2026-10-28. See HANDOFF.md for the verified source commit.

## Performed

- `bash scripts/cloud_setup.sh`: Release build plus unittest discovery. Final
  result: **24 tests passed, 0 failed, 0 skipped**, 22.620 seconds. Release build:
  **0 warnings, 0 errors**, 1.81 seconds. No third-party Python dependencies.
- `dotnet publish src/WinFix.Agent/WinFix.Agent.csproj -c Release -r win-x64 --self-contained true -o artifacts/win-x64`:
  passed; generated Windows x64 PE executable and bundled runtime. This is a build,
  NOT execution or compatibility validation on Windows.
- .NET SDK Linux archive SHA-512 verified against official Microsoft metadata.
- Git whitespace/error check before commit; source and configuration reviewed for
  credentials. Generated test credentials live only in temporary private directories.

Coverage includes real HTTPS agent startup and client requests; structured mock
results; token/device denial; expiry; stale/future timestamps; replay after restart;
concurrent replay; invalid/oversized requests; untrusted TLS and hostname mismatch;
stop, disconnect, full/corrupt audit; no command endpoint; bootstrap overwrite
refusal; non-Windows real-mode refusal; CLI failure on mock evidence; response
schema/correlation/freshness checks; redirects, malformed/oversized/non-JSON
responses and timeout redaction.

Initial 20 tests passed, then 22 after audit-corruption/platform guards were added.
The final suite also includes response-bound/timeout tests; use the final result
below, not earlier counts. Tests contain multiple cases and do not skip Windows
acceptance by silently treating mock output as Windows evidence.

## Not run / not established

Windows tests/GUI/installer/service, real Codex-to-Windows HTTPS request, private
Tailscale route, VPS relay, MCP discovery, fresh-task restoration, production security
assessment and GitHub Actions execution. No claims of repairs or certificate-error
resolution. The user confirmed no Windows test computer is available.

Official Codex/Tailscale documentation access returned proxy 403. Draft allowlist
updates are saved, but live access and publication are not verified. .NET first-use
initially failed on the read-only user directory; approved build access resolved it,
and the repeatable cloud setup script subsequently succeeded in the normal sandbox.

## Portable test artifact

Local ignored output: artifacts/winfix-phase0-win-x64-unsigned.zip (48,529,347 bytes).
SHA-256: `48fae48f33d600cddabe90ad5935bd5afa0d0cedf0a2aa086a947bfebbc3eb6b`.
The package is unsigned and Windows execution is untested. It is not a GitHub
release; rebuild from source or manually run the Windows workflow for CI artifacts.
