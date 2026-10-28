# Decisions

- **D001 — Phase 0 first.** Empty repository confirmed through GitHub and local refs.
  Bootstrap the supplied specification; do not invent recovered project history.
  No Windows host is available, so deliver a runnable real-machine gate without
  claiming it passed. Defer Phase 1 platform-specific collectors until that gate.
- **D002 — .NET 10 + Python standard library.** Use a supported .NET LTS family and
  a pinned SDK; no external agent/client libraries needed. One fixed system-info
  endpoint supplies useful evidence before introducing command execution.
- **D003 — HTTPS abstraction, private route conditional.** Verified local HTTPS
  first. Tailscale requires current official documentation, commercial licensing
  review and a real managed VPN integration test; no guessed native support.
  Relay is optional future work and would carry messages, not AI inference.
- **D004 — Foreground read-only owner session.** Random one-hour credential,
  separate IDs, local private files, durable nonce reservations, fixed operation,
  explicit stop. No service persistence, repair or elevation in this prototype.
- **D005 — Honest build/test boundaries.** Cross-built Windows package is not a
  validated Windows application. Linux mock evidence is marked and refused by the
  default client. Windows CI is manually triggered to avoid surprise quota usage.
- **D006 — Account-independent continuity.** Full specification and handoff live in
  Git, no secrets; branch pushes must not overwrite concurrent work. No paid AI API.
- **D007 — User-requested easy-install packaging.** Add a self-contained Windows EXE,
  per-user NSIS setup and visible English/Russian console menu while the remote
  Windows acceptance gate remains pending. Local diagnostics need no credentials;
  a local listener requires explicit consent. Retain private data on uninstall.
  GitHub REST release operations are blocked; upload the ~44 MB setup binary to a
  versioned downloads directory through working Git authentication, with checksums
  and source provenance. Release assets can replace this distribution path later.
