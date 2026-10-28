# WinFix AI handoff

- Project: WinFix AI, authorized Windows diagnostics and future assisted repair.
- Phase: Phase 0 locally tested prototype; real Windows/private-network gate pending.
- Active branch: feat/phase0-secure-diagnostics.
- Latest verified code commit: `e8cff88be1abf2e690053516abed316483803438`
  (`Implement Phase 0 read-only HTTPS diagnostics prototype`). A later documentation-only
  commit records this hash; use `git log -1` for the branch's documentation tip.
- GitHub continuity: the feature branch was pushed successfully and its remote SHA
  matched that code commit. Do not assume a main branch exists in this initially
  empty repository; explicitly select feat/phase0-secure-diagnostics when cloning.
- Verified results: 24 tests passed, 0 failed/skipped; Release build 0 warnings/errors;
  self-contained Windows x64 publish passed (Windows execution remains untested).
- Repository at start: empty local and remote refs. No earlier completed features
  were available. The user supplied the specification now saved as SPECIFICATION.md.

## Completed / incomplete

See PROJECT_STATUS.md and TEST_REPORT.md. Implemented actual .NET HTTPS host, owner
initialization, fixed read-only system-info operation, separate device/technician
identity, expiring credential, persistent replay reservation, bounded fail-closed
audit, local STOP, verified-TLS Python CLI, mock evidence guard, automated tests,
Windows cross-build and manual CI. No paid LLM API is used.

All Phase 1+ features remain incomplete, including service host, event logs/services,
repair approvals, certificate/CryptoPro diagnostics, UI automation, relay, dashboard,
and installer. Windows platform-specific code and portable executable are untested.

## Blockers and configuration

The user explicitly reported no Windows test machine. Real integration cannot be
claimed. Codex/Tailscale official documentation fetches returned proxy 403; the
environment draft adds developers.openai.com and tailscale.com. Review/save those
settings and publish as appropriate; saving the draft alone did not apply them.
No WINFIX/Tailscale credentials or target host are configured. Never ask for tokens
in chat or assume subscription entitlements are API credits.

This cloud checkout uses .NET under /workspace/.dotnet and Python 3.12.14. Run
`bash scripts/cloud_setup.sh` from /workspace/WinFix-AI. Tests create and stop temporary
HTTPS hosts. No persistent service, test credential, or connection should survive.
See SETUP.md for first-use directory permissions, portable launch and private routing.
The reusable environment configuration is to retain this checkout and SDK, run
scripts/cloud_setup.sh for installation/refresh, and read this handoff on startup.
Review/save and publication are separate from current-instance validation; a new
task's filesystem restoration and networking have not yet been tested.

## Exact continuation

1. Fetch origin, inspect git status/log and this feature branch; preserve concurrent
   work. Use the existing isolated checkout, not a worktree. Never force push.
2. Read AGENTS.md and every project-state document listed there. Verify the commit
   below against actual Git history before relying on this report.
3. Build and run `python -m unittest discover -s tests -v`; set DOTNET to the SDK
   executable if it is not on PATH. Record actual current results.
4. Highest-priority unfinished task: obtain an authorized Windows test host and
   supported private HTTPS route, review current official networking/licensing
   documentation, then run SETUP.md's Phase 0 real-Windows acceptance. Save sanitized
   evidence with OS version, tested commit and the exact route. Never use --allow-mock
   for that acceptance. Test owner ACLs and portable launch on Windows as well.
5. Only after that gate succeeds, implement the next P1 item: bounded read-only
   event-log inspection and service inventory with per-operation capabilities and
   Windows tests. Do not add arbitrary command execution or paid AI dependencies.
6. Update status/queue/issues/test report and this handoff; commit and push a feature
   branch. Confirm remote SHA. Another account must work from Git, not this chat.

If the Windows prerequisite is still missing, report that precise blocker instead
of claiming remote functionality or rebuilding the completed HTTPS prototype.
