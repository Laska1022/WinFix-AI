# WinFix AI handoff

- Project: WinFix AI, authorized Windows diagnostics and future assisted repair.
- Phase: Phase 0 locally tested prototype; real Windows/private-network gate pending.
- Active branch: fix/audit-journal-framing-20261104.
- Latest verified code commit: `96a40fc07af63ebfa68bf4a43477cfd1e3cd094e`
  (`Reject audit journals missing the final record delimiter`). This subsequent
  documentation-only commit records its hash; use `git log -1` for the documentation tip.
- GitHub continuity: select `fix/audit-journal-framing-20261104` for both audit fixes;
  `feat/phase0-secure-diagnostics` is the original prototype branch. Do not assume
  a main branch exists. Verify local HEAD against the selected remote branch when
  continuing work.
- Verified results for BUG-02 (including BUG-01): 29 tests passed, 0 failed/skipped; Release build
  0 warnings/errors. An earlier Windows x64 cross-publish passed; it was not repeated
  for this fix, and Windows execution remains untested.
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

## Bug review — 2026-11-04

The 2026-11-04 review branch is `review/phase0-bug-report-20261104`, based on source `bd78e2cc1ce4157e5d259a0f43824f6359fa1ed5`. Read [BUG_REPORT.md](BUG_REPORT.md): three bugs were reproduced while all 24 existing tests passed. BUG-01 and BUG-02 have since been fixed on `fix/audit-journal-framing-20261104`; see the verified code commit above and TEST_REPORT.md for the 29-test result. Next: fix and regression-test BUG-03, then continue the outstanding owner-authorized Windows/private-route acceptance; the Windows prerequisite remains unresolved.
