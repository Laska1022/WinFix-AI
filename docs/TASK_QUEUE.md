# Task queue

## P0 — Finish Phase 0 acceptance

1. Review current official Codex Cloud network/VPN and Tailscale documentation and
   commercial licensing after the documentation allowlist change is applied.
2. Obtain an owner-authorized Windows 10/11 x64 test host, matching HTTPS certificate,
   and supported private route. User currently has no test host available.
3. Run build and all tests on Windows. Exercise the published portable application
   and validate bootstrap ACLs, least-privilege startup and uninstall procedure.
4. From Codex run SETUP.md's real HTTPS acceptance, negative authorization, stop,
   expiry, and restart replay checks. Record sanitized evidence and exact commit.
5. Verify a fresh Codex task can restore/build the repository and repeat the route.

Do not call Phase 0 complete until these required gates pass. A code-only task
without a Windows host can strengthen protocol tests/documentation, but must not
replace real integration evidence with mocks.

## P1 — Windows Agent MVP, after P0

Add bounded read-only Windows event-log inspection (fixed channels, time range and
record count; redact sensitive fields), service inventory, and allowlisted diagnostic
operations. Add per-operation capabilities before expanding the API. Implement and
test foreground/service lifecycle and separate explicitly authorized elevation for
future operations. No arbitrary PowerShell input.

## Later ordered work

- Approved repair state machine, policy, cancellation, persisted case history,
  verification and explicit rollback limits.
- Certificate/CryptoPro diagnostics and DLG_FLAGS_INVALID_CA evidence workflow:
  date/time, chain/root/intermediate/expiry/revocation/proxy checks, never TLS bypass.
- Interactive desktop companion with visible consent and secure-session limits.
- Research/repair/report workflows and searchable local knowledge base.
- English/Russian responsive dashboard, approvals, emergency stop.
- Optional outbound relay, secure enrollment/revocation, installer, signing and
  Windows Server/Server Core matrix; production security review.
