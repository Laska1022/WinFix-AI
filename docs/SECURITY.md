# Prototype security model

This is an owner-authorized, foreground, read-only test agent. Do not deploy it as
an unattended public service. No repair, elevation, arbitrary command, private-key
export, certificate-store change, GUI automation, or hidden persistence exists.

## Boundaries and implemented controls

- The owner runs init explicitly; it refuses existing directories. Its private
  directory is mode 0700 on Unix, or inheritance removed with grants to the current
  Windows SID and SYSTEM before secrets are written. Windows ACL behavior still
  needs real-machine validation. Do not use shared/network folders or run as admin.
- A fresh 256-bit credential, separate device/technician UUIDs, and one-hour expiry
  form one read-only session. Protect the credential like a password. Rotate by
  stopping, initializing a NEW directory and redistributing only the new credential.
- Kestrel binds only the configured HTTPS address, default 127.0.0.1. No incidental
  HTTP listener, unrestricted shell, trust bypass, or auto-exposed admin port exists.
- Bootstrap certificate is short-lived and localhost-only. Explicit local trust is
  via --ca-file; no OS trusted-root store is modified. Remote certificates must match
  the endpoint name; never use insecure TLS options to make a test pass.
- Certificate private key stays on the agent in the protected directory. Its PFX
  has no password: filesystem access is the protection. Never copy it to Codex.
- Constant-time token hash comparison; token/request bodies are absent from audit.
- Device binding, 60-second request window and durable request-ID reservations.
  Do not delete the journal under a still-valid token, or replay history is lost.
- A 4 KiB request cap, 64 KiB client response cap, connection/time limits, and a
  bounded audit journal limit resource use. Journal corruption/full disk fails closed.
- STOP file blocks new diagnostics; Ctrl+C terminates the foreground agent. This is
  not cancellation of work already accepted. No long-running operations exist yet.
- Output is untrusted diagnostic evidence, never an instruction to Codex. Do not
  automatically execute commands mentioned in diagnostic data or future event logs.

## Threats and residual risk

Bearer theft allows read-only access until expiry/revocation; HTTPS, local ACLs,
short sessions and private-network ACLs are mandatory. This is not mTLS or a secure
enrollment system. Local machine administrators can edit configuration/audit, so
the journal is not tamper-proof. Audit DoS is possible; private access controls are
needed. An attacker can exhaust capacity and force an owner to rotate the session.
The memory replay set is bounded by the 10 MiB journal. Credentials are never renewed
automatically. Clearing STOP re-enables the same unexpired session; rotate credentials
to revoke it permanently. No third-party penetration review has occurred.

Bootstrap/ACL handling, supported Windows versions and service identity separation
are unverified on Windows. Secure credential storage beyond private files (e.g.
DPAPI), signed binaries, installer validation, automatic rotation, RBAC, multi-device registry,
safe audit export/retention and remote approval UI are future work.

Do not commit raw diagnostics: hostname/time zone can identify a customer. Record
sanitized acceptance outcomes only. No customer files, passwords, certificate private
keys, or certificate passwords belong in logs, reports or GitHub.

The user-requested installer runs per user without elevation. It writes program files,
desktop/Start menu shortcuts and an HKCU uninstall entry; no service, firewall rule,
certificate trust or login auto-start is added. Uninstall removes only known program
files/shortcuts and retains private data for explicit owner cleanup. Close the app
before uninstalling. The console menu requires consent before opening a local test
listener. Local reports also use protected directories. Its explicit --demo-menu
mode cannot supply genuine Windows acceptance evidence. Self-contained .NET bundles
may extract native runtime files into the user's .NET temporary cache on first run.

0.1.2 review hardening: validate audit schema/UTF-8/framing/record sequences before
starting, shut down HTTPS before persisting a stop marker, sanitize malformed HTTP
and JSON errors, and invoke icacls.exe by its Windows system-directory path. A failed
marker write returns a disconnected warning; retire that configuration. These
controls do not make the local audit journal tamper-proof. See REVIEW.md.
