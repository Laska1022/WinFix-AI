# Architecture

## Implemented Phase 0 path

Codex shell / technician -> Python HttpsTransport -> configured HTTPS proxy or
local direct HTTPS -> Kestrel agent -> fixed read-only .NET system information.

The .NET 10 host targets net10.0 to allow protocol tests on Linux. Real collection
refuses to start outside Windows. Mock mode must be explicitly enabled in local
configuration and is labeled in every result. Windows x64 is the first intended
target; Windows 10/11 and Server 2016+ compatibility remains untested.

The only diagnostic endpoint is POST /v1/diagnostics/system. Its JSON request has
deviceId, requestId (UUID), and issuedAt (UTC, within 60 seconds). Authorization
uses a 256-bit random bearer credential over verified TLS. The owner assigns a
device ID and a distinct technician ID; server configuration contains the token
SHA-256, not the token. Credentials expire within one hour of initialization.

Audit reservations are flushed to disk before collection. A persistent request-ID
set prevents replay after restart; repeated concurrent requests have one winner.
Completed records precede responses. The maximum journal is 10 MiB: full or corrupt
journals fail closed. The owner must archive and rotate credentials before resetting
a journal. This is a prototype single-technician, single-device session, not a
multi-tenant authorization service.

The response includes schemaVersion, request correlation, device ID, collection
time, mock marker, and OS/name/architecture/uptime/time-zone fields. The client
validates identity, schema, freshness and Windows-vs-mock evidence. No shell runs.

## Transport decision

HTTPS is the verified application protocol. Python urllib honors configured proxy
variables, keeps TLS verification on, refuses redirects, and caps response size.
It does not assume raw TCP, WebSockets, persistent processes, or a local VPN daemon
in Codex. Local loopback uses an explicitly trusted test certificate. A private
deployment must supply a certificate matching its private DNS name and an
authorized HTTPS route in the environment. There is no HTTP fallback.

Tailscale is the preferred deployment candidate, conditional on actual managed VPN
support in the user's Codex environment. We have not established such a route.
The provided cloud onboarding contract says VPN is platform-managed in an egress
proxy sidecar; it specifically does not call for installing a VPN client here.
See FEASIBILITY.md for observations, sources, and the comparison with a VPS relay.

## Deferred components

- Phase 1: Windows Service host, event logs, services, named read-only diagnostics.
- Phase 2: operation policy, approval records, repair/elevation broker, cancellation,
  verification and bounded rollback. Current credentials grant no repair capability.
- Phase 3: interactive desktop companion and authenticated service-to-desktop IPC;
  never UAC/secure-desktop bypass or automation of a locked session.
- Phase 4: resumable cases and local searchable knowledge base without paid embeddings.
- Phase 5: English/Russian dashboard, approvals and emergency stop.
- Phase 6: signed packaging, installers, revocation/rotation, security and OS matrix.
- Optional relay: outbound agent polling over HTTPS, separate device and technician
  identities, scoped expiring jobs, no AI inference. Transport interface exists;
  relay delivery, persistence, and multi-device identity do not yet exist.

MCP is not implemented. CLI use requires no assumption of identical MCP support
across Codex Cloud, CLI, and desktop.
