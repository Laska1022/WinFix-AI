# Project status

## Phase 0 — local prototype implemented; remote acceptance pending

Implemented: owner-initialized read-only .NET HTTPS agent; actual Windows collector
code with explicit Linux mock mode; Python CLI/HTTPS transport interface; expiring
credential and device binding; persisted replay protection; bounded audit journal;
local stop; portable Windows cross-build; reproducible tests; manual Windows/Linux
CI workflow; full architecture, setup, threat model and account-independent handoff.

Linux build and integration checks pass. No Windows host is available. Neither the
real Windows diagnostics path nor Codex-to-Windows networking has been verified.
Do not call Phase 0 complete or proceed as though Phase 1's prerequisite passed.
See TEST_REPORT.md for the precise current test results and HANDOFF.md for commits.

Deferred: Windows Service mode, event logs/services/PowerShell diagnostics, repairs,
approval/elevation, certificate/CryptoPro diagnostics, GUI companion, relay, dashboard,
knowledge base, installer and production hardening. No paid AI dependency exists.

Next: P0 acceptance in TASK_QUEUE.md. First unblock official documentation access
and obtain an owner-authorized Windows test host/private HTTPS route. Default client
refuses mock evidence, so it can serve as the real connection acceptance command.
