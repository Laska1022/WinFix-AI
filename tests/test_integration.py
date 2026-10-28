"""Exercise the actual .NET HTTPS host, with explicit mock diagnostics on Linux."""
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
import uuid

from tools.winfix_client import HttpsTransport, WinFixError, get_system_information

ROOT = Path(__file__).resolve().parents[1]
DLL = ROOT / "src/WinFix.Agent/bin/Release/net10.0/WinFix.Agent.dll"
DOTNET = os.environ.get("DOTNET", "dotnet")


class AgentIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "private"
        subprocess.run([DOTNET, str(DLL), "init", str(self.directory)], check=True, capture_output=True)
        self.path = self.directory / "agent.json"
        self.config = json.loads(self.path.read_text())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.config["Port"] = sock.getsockname()[1]
        self.config["Mock"] = os.name != "nt"
        self.original_config = self.config.copy()
        self.url = f'https://127.0.0.1:{self.config["Port"]}'
        self.token = (self.directory / "client-token.txt").read_text()
        self.cert = self.directory / "server-cert.pem"
        self.context = ssl.create_default_context(cafile=str(self.cert))
        # These are local tests, regardless of a developer's ambient proxy settings.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=self.context))
        self.process = None
        self.addCleanup(self.stop)
        self.start()

    def start(self):
        self.path.write_text(json.dumps(self.config))
        self.process = subprocess.Popen([DOTNET, str(DLL), "serve", str(self.path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail("Agent exited during startup")
            try:
                with self.opener.open(self.url + "/not-found", timeout=.5):
                    pass
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    return
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(.05)
        self.fail("Agent did not become ready")

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process = None

    def payload(self):
        return {"deviceId": self.config["DeviceId"], "requestId": str(uuid.uuid4()),
                "issuedAt": dt.datetime.now(dt.timezone.utc).isoformat()}

    def send(self, payload=None, token=None, path="/v1/diagnostics/system"):
        body = json.dumps(self.payload() if payload is None else payload).encode()
        request = urllib.request.Request(self.url + path, data=body,
                                         headers={"Content-Type": "application/json", "Authorization": "Bearer " + (self.token if token is None else token)})
        try:
            with self.opener.open(request, timeout=5) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            return exc.code, json.loads(raw) if raw else {}

    def client(self):
        client = HttpsTransport(self.url, self.token, str(self.cert))
        client.opener = self.opener
        return client

    def test_structured_diagnostics_and_audit(self):
        result = get_system_information(self.client(), self.config["DeviceId"], allow_mock=os.name != "nt")
        self.assertEqual(result["system"]["platform"], "Windows" if os.name == "nt" else "Mock")
        records = [json.loads(line) for line in Path(self.config["AuditPath"]).read_text().splitlines()]
        self.assertEqual([r["Outcome"] for r in records], ["accepted", "completed"])
        self.assertEqual(records[-1]["TechnicianId"], self.config["TechnicianId"])
        self.assertNotIn(self.token, Path(self.config["AuditPath"]).read_text())

    def test_bad_token_and_device_denied(self):
        self.assertEqual(self.send(token="wrong")[0], 401)
        payload = self.payload(); payload["deviceId"] = str(uuid.uuid4())
        self.assertEqual(self.send(payload)[0], 403)

    def test_expired_credential(self):
        self.stop()
        self.config["ExpiresAt"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)).isoformat()
        self.start()
        self.assertEqual(self.send()[0], 401)

    def test_replay_rejected_across_restart(self):
        payload = self.payload()
        self.assertEqual(self.send(payload)[0], 200)
        self.assertEqual(self.send(payload)[0], 409)
        self.stop(); self.start()
        self.assertEqual(self.send(payload)[0], 409)

    def test_concurrent_replay(self):
        payload = self.payload()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(lambda _: self.send(payload)[0], range(4)))
        self.assertEqual(sorted(statuses), [200, 409, 409, 409])

    def test_stale_and_future_requests(self):
        for seconds in (-120, 120):
            payload = self.payload()
            payload["issuedAt"] = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=seconds)).isoformat()
            self.assertEqual(self.send(payload)[0], 400)

    def test_emergency_stop(self):
        Path(self.config["StopFile"]).touch()
        self.assertEqual(self.send()[0], 503)

    def test_no_command_endpoint(self):
        self.assertEqual(self.send({"command": "whoami"}, path="/v1/execute")[0], 404)

    def test_invalid_and_oversized_requests(self):
        self.assertEqual(self.send({"requestId": "invalid"})[0], 400)
        self.assertEqual(self.send({"padding": "x" * 5000})[0], 413)

    def test_untrusted_tls_rejected(self):
        client = HttpsTransport(self.url, self.token)
        client.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        with self.assertRaises(WinFixError):
            client.post(self.payload())

    def test_hostname_verification(self):
        with socket.create_connection(("127.0.0.1", self.config["Port"])) as sock:
            with self.assertRaises(ssl.SSLCertVerificationError):
                self.context.wrap_socket(sock, server_hostname="wrong.example")

    def test_disconnected_agent(self):
        self.stop()
        with self.assertRaises(WinFixError):
            self.client().post(self.payload())

    def test_audit_full_fails_closed(self):
        self.stop()
        # Valid journal just below its bound; next acceptance must fail, on Windows too.
        entry = json.dumps({"At": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "RequestId": None, "TechnicianId": None, "Outcome": "test"})
        padding = " " * (10 * 1024 * 1024 - len(entry) - 10)
        Path(self.config["AuditPath"]).write_text(entry + padding + "\n")
        self.start()
        self.assertEqual(self.send()[0], 503)

    def test_corrupt_audit_refuses_startup(self):
        self.stop()
        Path(self.config["AuditPath"]).write_text("{interrupted write")
        result = subprocess.run([DOTNET, str(DLL), "serve", str(self.path)], capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_real_mode_requires_windows(self):
        if os.name == "nt":
            self.assertEqual(self.send()[1]["system"]["platform"], "Windows")
            return
        self.stop()
        self.config["Mock"] = False
        self.path.write_text(json.dumps(self.config))
        result = subprocess.run([DOTNET, str(DLL), "serve", str(self.path)], capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_bootstrap_never_overwrites(self):
        result = subprocess.run([DOTNET, str(DLL), "init", str(self.directory)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.directory / "client-token.txt").read_text(), self.token)

    def test_cli_and_real_evidence_requirement(self):
        command = [os.sys.executable, str(ROOT / "tools/winfix_client.py"), "get-system-information",
                   "--endpoint", self.url, "--device-id", self.config["DeviceId"], "--ca-file", str(self.cert)]
        environment = dict(os.environ, WINFIX_TOKEN=self.token, NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")
        result = subprocess.run(command, env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if os.name == "nt" else 1)
        result = subprocess.run(command + ["--allow-mock"], env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["deviceId"], self.config["DeviceId"])


if __name__ == "__main__":
    unittest.main()
