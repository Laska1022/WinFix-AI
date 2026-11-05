# Known issues and limitations

- No Windows test machine: Windows collection, ACLs, portable execution, and Windows
  10/11/Server support are not verified. Phase 0's remote acceptance is blocked.
- Official Codex/Tailscale documentation requests were denied by the proxy. Domain
  additions are saved in the environment draft, not proven applied. No VPN, private
  HTTPS route, TCP route, MCP compatibility or commercial license limits verified.
- Local bootstrap certificate only names localhost/127.0.0.1. Remote use requires
  operator provisioning of a matching certificate and protected PFX. No wizard yet.
- One technician/device/session, bearer auth, private file credentials. No DPAPI,
  automated enrollment, RBAC, mTLS, renewal, unattended mode, installer or service.
- STOP refuses new work but cannot cancel a request already accepted. No long-running
  commands are implemented. Permanent revocation requires retiring the session.
- Audit is bounded and durable but not tamper-proof. Full/corrupt journals stop
  diagnostics; archive and rotate credentials before resetting, never silently repair.
- Diagnostics include machine identity; protect output and sanitize committed reports.
- .NET build initially needed approved access outside the read-only cloud home;
  setup instructions record this. A new task's restore/build has not been tested.
- Windows CI is supplied but has not run. A Linux cross-build is not a Windows test.
- All repair modules, certificate/CryptoPro diagnosis, GUI, dashboard, relay, approval
  workflows and production packaging remain unfinished. No paid AI API is required.

## Bug review — 2026-11-04

BUG-01 (incomplete audit entries accepted) is fixed in code commit `a2bdfc1d482d51df3c078cb4a729dbdf1e209817`. BUG-02 (missing final journal delimiter) is fixed in code commit `96a40fc07af63ebfa68bf4a43477cfd1e3cd094e`. BUG-03 (client protocol errors) is fixed in code commit `a43738bdf1d68a063555954d8fbee5be1ad7aa7e`. All three findings in [BUG_REPORT.md](BUG_REPORT.md) are resolved on `fix/client-protocol-errors-20261104`, pending review/merge. The audit reproductions require local file damage/modification. Invalid existing audit records or missing final delimiters must be handled through the documented archive/session-rotation procedure; startup does not silently repair them.

## Download distribution — 2026-11-05

GitHub Releases API access still returns Forbidden in the current runtime. Repository-hosted binaries are provided as an interim download path; no GitHub Release publication is claimed.
