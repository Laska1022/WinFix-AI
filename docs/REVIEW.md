# Reliability review — 2026-10-28

Reviewed the implemented agent, Python client, audit journal, menu lifecycle,
installer source, build scripts and tests. Baseline: 29 tests passed on the original
0.1.1 preview. These checks do not cover the unimplemented product phases and are
not a penetration test or proof that the Windows installer runs correctly.

## Reproduced and fixed

| Problem | Reproduction before fix | Corrected behavior |
| --- | --- | --- |
| Stop depended on writable session storage | Make STOP a directory: unhandled exception; move the session directory during a Linux session: Enter leaves the process waiting for another input | Shut down HTTPS before writing STOP; a failed marker write returns a clear disconnected warning and nonzero status. Cleanup also stops the host on exceptions. |
| Corrupt audit state accepted on restart | Replace the journal with a valid JSON object missing its fields (`{}`): agent starts instead of refusing recovery | Require exact fields, valid IDs, recognized outcomes, strict UTF-8, complete newline-terminated records, unique reservations and matching completions. Close the file on recovery failure. |
| HTTP protocol errors escape the client | BadStatusLine and IncompleteRead escape as exceptions instead of WinFixError | Treat malformed/truncated HTTP as sanitized connection failures; deeply nested JSON becomes an invalid-response error. Close HTTP error responses. |
| False readiness message | Launch a separately initialized agent on an occupied port: prints READ ONLY active before startup fails | Announce readiness only after Kestrel has started successfully. |

Additional hardening: invoke icacls.exe through the Windows system directory rather
than executable search paths. This change compiles but still needs Windows runtime
validation. Expected client failures now show their safe error messages (such as
HTTP 401) instead of collapsing every diagnosis into the same generic sentence.

## Verification

`bash scripts/cloud_setup.sh`: **37 passed, 0 failed, 0 skipped**, 32.888 seconds;
Release build: **0 warnings, 0 errors**. New cases cover the failures above, nine
malformed audit variants and restart after a valid unfinished audit reservation.
Existing tests still verify credential expiry, unauthorized devices, TLS verification,
concurrent/restarted replay, limits, mock markers and ordinary menu operation.

The moved-directory scenario is Linux-specific and is explicitly skipped on Windows,
where an open journal may lock the directory. The marker-write failure test runs on
both platforms. Windows tests have not been executed in this environment.

Reproductions failed against the original implementation before fixes; all current
checks passed afterward. Packaging evidence and exact build provenance accompany
the versioned 0.1.2 preview download. The 0.1.1 download/tag are preserved.

## Remaining limits

No real Windows host/private route, GUI or repair validation, installation/uninstallation
execution, or Windows ACL test is available. Audit records remain owner-controlled,
not tamper-proof: deleting an entire valid record is not detectable without a trusted
external anchor. Do not reset a journal under an unexpired credential. If a stop marker
cannot be written, retire that session configuration instead of restarting it.
