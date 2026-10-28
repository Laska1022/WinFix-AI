# WinFix AI development instructions

Read docs/ARCHITECTURE.md, PROJECT_STATUS.md, HANDOFF.md, TASK_QUEUE.md,
KNOWN_ISSUES.md, SECURITY.md, and TEST_REPORT.md before implementing work.
The complete user requirements are in docs/SPECIFICATION.md.

- Use the existing checkout. Each Codex task is isolated; do not create worktrees
  unless the user explicitly requests one. Check status, fetch, and inspect remote
  branches before changing anything. Preserve other work; never force push.
- Work on a uniquely named feature branch. Commit focused changes and push the
  branch when authorized; do not assume an uncommitted workspace transfers accounts.
- No paid AI API, undocumented ChatGPT tokens, subscription bypass, or automatic
  Codex-task initiation. The agent and CLI must work without AI.
- No arbitrary command API, stealth, private-key export, UAC bypass, disabling
  TLS/HSTS/security controls, or unverified trusted-root installation.
- Keep diagnostic operations read-only. Repairs require action-specific approvals,
  least privilege, audit, verification, and honest rollback limits in later phases.
- Never commit credentials, PFX files, customer diagnostics, or private machine names.
  Keep them outside the checkout or under ignored .local/.
- Build: `dotnet build src/WinFix.Agent/WinFix.Agent.csproj -c Release`.
  Test: `python -m unittest discover -s tests -v` (Python 3.12+, .NET pinned in global.json).
  Cloud shortcut: `bash scripts/cloud_setup.sh`; see SETUP for sandbox requirements.
- Linux integration tests use the actual HTTPS agent with explicit mock diagnostics.
  They do NOT prove Windows functionality, private routing, GUI automation, or repair.
  Keep real-Windows acceptance separate and do not silently skip tests.
- Update status, queue, known issues, decisions, test report, and handoff at each
  milestone. Record exact commands, results, branch, blockers, and next task.
  Record a verified code commit in a subsequent documentation-only commit to avoid
  claiming a self-referential commit hash. Never claim CI ran without its results.

Current scope: complete Phase 0's real Windows HTTPS acceptance before Phase 1.
