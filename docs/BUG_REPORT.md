# Confirmed bug report — Phase 0

Review date: 2026-11-04. Reviewed source commit:
`bd78e2cc1ce4157e5d259a0f43824f6359fa1ed5`.
Report branch: `review/phase0-bug-report-20261104`.

Reviewed the agent bootstrap, HTTPS endpoint, audit journal, Python client,
existing tests and project documentation. This is a bounded code review, not a
complete security assessment. All three findings below were reproduced locally.
Application code has not been changed; these bugs remain open.

## BUG-01 — Incomplete audit records are silently accepted (medium)

Location: `src/WinFix.Agent/AuditJournal.cs:19-22`.

The journal loader deserializes records without checking required fields. A JSON
object such as `{}` becomes an entry with default/null fields. It is ignored
because its Outcome is not `accepted`, instead of causing startup to fail.

Reproduction:

1. Initialize a temporary mock agent; send a valid diagnostic request (HTTP 200).
2. Stop it and replace that request's `accepted` journal line with `{}`, retaining
   the `completed` line. This deliberately simulates a damaged journal.
3. Restart and resend the identical request while its timestamp is still valid.

Observed: startup succeeds and the reused request ID returns **HTTP 200**, rather
than being rejected. Expected: a structurally invalid audit journal prevents
startup, consistent with the documented fail-closed policy.

Impact: replay history can be silently lost when syntactically valid but
structurally incomplete audit records are loaded. This reproduction requires
local journal corruption or modification; it is **not** evidence that a remote
caller can edit the journal or bypass bearer authentication. Administrator
tampering remains outside the stated tamper-resistance guarantees.

Suggested fix: validate timestamps, required fields, outcome values and
outcome-specific request/technician IDs before accepting existing records. Reject
invalid records and require the documented archive/session-rotation procedure.
Add regression coverage for valid JSON with missing or null required fields.

## BUG-02 — Missing final newline causes delayed journal corruption (medium)

Location: `src/WinFix.Agent/AuditJournal.cs:19-24,42-45`.

`ReadLine()` accepts a final JSON record without a newline. The writer then seeks
to the exact end and appends another record without inserting a separator. Two
JSON objects become one invalid JSON line.

Reproduction:

1. Send one successful request, stop the agent and remove only the journal's final
   newline, keeping all JSON records intact.
2. Restart and send a fresh request: both operations succeed (HTTP 200).
3. Stop and restart again.

Observed: the second restart terminates with **JsonException** because the
previously valid final record and the next appended record were concatenated.
Expected: reject an unterminated journal before serving requests, or apply an
explicitly designed durable framing policy that preserves all replay history.

Impact: a damaged/truncated delimiter can appear harmless on the first startup
and become an availability failure on the next one. The reproduction simulates
file damage; an actual power-loss scenario was not tested.

Suggested fix: validate record boundaries before appending. Under the current
fail-closed policy, reject a missing final delimiter and require owner-directed
archive/session rotation. Add a restart/append/restart regression case. Do not
silently delete history or reset an active session's journal.

## BUG-03 — Malformed HTTPS status escapes safe client error handling (medium)

Location: `tools/winfix_client.py:53-61` and the exception handler in `main()`.

Neither exception handler catches `http.client.HTTPException`.
`http.client.BadStatusLine` inherits from it, not from the exceptions currently
caught. A TLS-authenticated peer can therefore cause an uncaught traceback.

Reproduction: connect the real CLI to a temporary HTTPS fixture with an explicitly
trusted localhost certificate. Read the complete request, then send
`SYNTHETIC_SERVER_PRIVATE_MARKER\r\n\r\n` instead of a valid HTTP status line.

Observed: CLI exits 1 with an uncaught **BadStatusLine** traceback containing the
synthetic marker. Expected: the usual generic failure message, without reflecting
arbitrary server-controlled text. Certificate and hostname verification remained
enabled throughout the reproduction.

Impact: malformed responses produce a traceback and expose peer-provided text in
terminal/log output. This does not demonstrate disclosure of a real token or
customer information; the demonstration used only a synthetic marker.

Suggested fix: translate HTTP protocol exceptions into a safe `WinFixError` with
suppressed exception chaining, and exercise the actual CLI against malformed
status/header/chunk framing. Preserve TLS verification and existing size limits.

## Validation and limitations

- `bash scripts/cloud_setup.sh`: Release build succeeded with 0 warnings/errors;
  **24 tests passed, 0 failed, 0 skipped**, 15.993 seconds for the test suite.
- Targeted reproductions below: BUG-01, BUG-02 and BUG-03 observed. These checks
  assert the current buggy behavior; success means reproduction, not remediation.
- Debian Linux x64, Python 3.12.14, .NET SDK 10.0.403 / runtime 10.0.14.
- Local HTTPS agents used explicit mock diagnostics and disposable private
  sessions. No customer data, saved credentials or global trust changes were used.
- Scoped execution permission was required for loopback sockets in this cloud
  sandbox. Windows execution, private networking and GitHub Actions were not run.
- Missing Windows acceptance, GUI, service mode and repairs are existing project
  limitations/deferred scope, not newly discovered implementation bugs.

## Reproduction script

Build with `bash scripts/cloud_setup.sh` from `/workspace/WinFix-AI`, then copy
this script to `/tmp/winfix_review.py` and run from the checkout root:

```sh
DOTNET=/workspace/.dotnet/dotnet DOTNET_CLI_HOME=/workspace/.dotnet-home python3 /tmp/winfix_review.py
```

The script needs OpenSSL and permission to bind loopback sockets. It uses the
existing integration-test fixture, generates temporary test credentials and
cleans up its processes/directories. Do not run it against a real session.

```python
import json, os, pathlib, socket, ssl, subprocess, sys, tempfile, threading
sys.path.insert(0, str(pathlib.Path.cwd()))
from tests.test_integration import AgentIntegration, DOTNET, DLL

def audit_checks():
    for mode in ('missing_fields', 'missing_newline'):
        t = AgentIntegration('test_structured_diagnostics_and_audit')
        try:
            t.setUp()
            payload = t.payload()
            assert t.send(payload)[0] == 200
            t.stop()
            p = pathlib.Path(t.config['AuditPath'])
            if mode == 'missing_fields':
                rows = p.read_text().splitlines()
                rows[0] = '{}'
                p.write_text('\n'.join(rows)+'\n')
                t.start()
                status = t.send(payload)[0]
                assert status == 200
                print('BUG-01: incomplete audit record accepted; previously used request ID returns HTTP', status)
            else:
                p.write_text(p.read_text().rstrip('\n'))
                t.start()
                assert t.send()[0] == 200
                t.stop()
                r = subprocess.run([DOTNET, str(DLL), 'serve', str(t.path)], capture_output=True, timeout=10)
                assert r.returncode != 0 and b'JsonException' in r.stderr
                print('BUG-02: missing final newline permits start and request, then next startup fails with JsonException')
        finally:
            t.doCleanups()

def client_check():
    with tempfile.TemporaryDirectory() as d:
        cert, key = str(pathlib.Path(d)/'cert.pem'), str(pathlib.Path(d)/'key.pem')
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',key,'-out',cert,'-days','1','-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1'],check=True,capture_output=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0)); listener.listen()
            port = listener.getsockname()[1]
            def respond():
                conn, _ = listener.accept()
                with context.wrap_socket(conn, server_side=True) as conn:
                    data = b''
                    while b'\r\n\r\n' not in data:
                        data += conn.recv(8192)
                    header, body = data.split(b'\r\n\r\n', 1)
                    size = next(int(line.split(b':',1)[1]) for line in header.split(b'\r\n') if line.lower().startswith(b'content-length:'))
                    while len(body) < size:
                        body += conn.recv(8192)
                    conn.sendall(b'SYNTHETIC_SERVER_PRIVATE_MARKER\r\n\r\n')
            thread = threading.Thread(target=respond, daemon=True); thread.start()
            env = dict(os.environ, WINFIX_TOKEN='synthetic-test-credential', NO_PROXY='127.0.0.1', no_proxy='127.0.0.1')
            r = subprocess.run([sys.executable,'tools/winfix_client.py','get-system-information','--endpoint',f'https://127.0.0.1:{port}','--device-id','00000000-0000-0000-0000-000000000001','--ca-file',cert],env=env,capture_output=True,text=True,timeout=15)
            thread.join(2)
            assert r.returncode == 1 and 'Traceback' in r.stderr and 'BadStatusLine' in r.stderr and 'SYNTHETIC_SERVER_PRIVATE_MARKER' in r.stderr
            print('BUG-03: verified HTTPS malformed status produces uncaught BadStatusLine traceback containing synthetic server marker')
audit_checks()
client_check()
```
