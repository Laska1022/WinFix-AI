# Known issues and limitations

- No Windows test machine: Windows collection, ACLs, portable execution, and Windows
  10/11/Server support are not verified. Phase 0's remote acceptance is blocked.
- Official Codex/Tailscale documentation requests were denied by the proxy. Domain
  additions are saved in the environment draft, not proven applied. No VPN, private
  HTTPS route, TCP route, MCP compatibility or commercial license limits verified.
- Local bootstrap certificate only names localhost/127.0.0.1. Remote use requires
  operator provisioning of a matching certificate and protected PFX. The new menu
  simplifies local operation only; remote enrollment has no wizard yet.
- One technician/device/session, bearer auth, private file credentials. No DPAPI,
  automated enrollment, RBAC, mTLS, renewal, unattended mode or service.
- STOP refuses new work but cannot cancel a request already accepted. No long-running
  commands are implemented. Permanent revocation requires retiring the session.
- Audit is bounded and durable but not tamper-proof. Full/corrupt journals stop
  diagnostics; archive and rotate credentials before resetting, never silently repair.
- Diagnostics include machine identity; protect output and sanitize committed reports.
- .NET build initially needed approved access outside the read-only cloud home;
  setup instructions record this. A new task's restore/build has not been tested.
- Windows CI is supplied but has not run. A Linux cross-build is not a Windows test.
- New per-user installer is unsigned. Windows installation, shortcuts, uninstall,
  runtime extraction, and SmartScreen behavior need real Windows validation.
- GitHub release API returned Forbidden despite existing authentication; Git pushes
  work. The setup EXE is distributed in the downloads directory on the feature branch,
  not as a GitHub Release asset. Moving binaries to Releases is future housekeeping.
- All repair modules, certificate/CryptoPro diagnosis, GUI, dashboard, relay, approval
  workflows and production packaging remain unfinished. No paid AI API is required.
