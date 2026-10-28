import json
import os
from pathlib import Path
import queue
import ssl
import subprocess
import tempfile
import threading
import unittest
import urllib.request

from tests.test_integration import DLL, DOTNET
from tools.winfix_client import HttpsTransport, WinFixError, get_system_information


class MenuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "data"
        self.environment = dict(os.environ, WINFIX_DEMO_DATA_DIR=str(self.root))

    def run_menu(self, user_input, *, demo=True):
        args = [DOTNET, str(DLL)] + (["--demo-menu"] if demo else [])
        return subprocess.run(args, input=user_input, text=True, encoding="utf-8", capture_output=True,
                              env=self.environment, timeout=15)

    def test_report_in_both_languages_without_credentials(self):
        for language in ("1", "2"):
            result = self.run_menu(language + "\n1\n0\n")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DEMO", result.stdout)
        reports = list(self.root.glob("Reports/*/system-information.json"))
        self.assertEqual(len(reports), 2)
        for path in reports:
            report = json.loads(path.read_text())
            self.assertTrue(report["mock"])
            self.assertEqual(report["system"]["platform"], "Mock")
            if os.name != "nt":
                self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(list(self.root.rglob("client-token.txt")), [])

    def test_declining_session_creates_no_credentials(self):
        result = self.run_menu("1\n2\nNO\n0\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.root.exists())

    def test_eof_and_unknown_option(self):
        result = self.run_menu("1\nwrong\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Choose 1, 2 or 0", result.stdout)
        self.assertFalse(self.root.exists())

    def test_real_launcher_platform_guard(self):
        result = self.run_menu("0\n", demo=False)
        self.assertEqual(result.returncode, 0 if os.name == "nt" else 1)
        self.assertFalse(self.root.exists())

    def test_explicit_session_consent_request_and_stop(self):
        self.exercise_session_stop(break_stop_marker=False)

    def test_stop_disconnects_even_when_marker_cannot_be_written(self):
        self.exercise_session_stop(break_stop_marker=True)

    @unittest.skipIf(os.name == "nt", "Windows can lock a directory containing an open audit file")
    def test_stop_disconnects_after_session_directory_moves(self):
        self.exercise_session_stop(break_stop_marker=True, move_directory=True)

    def exercise_session_stop(self, *, break_stop_marker, move_directory=False):
        process = subprocess.Popen([DOTNET, str(DLL), "--demo-menu"], env=self.environment,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8")
        output = []
        lines = queue.Queue()

        def read_output():
            for line in process.stdout:
                output.append(line)
                lines.put(line)

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        try:
            process.stdin.write("1\n2\nSTART\n")
            process.stdin.flush()
            for _ in range(25):
                if "LOCAL SESSION ACTIVE" in lines.get(timeout=10):
                    break
            else:
                self.fail("No readiness message")
            paths = list(self.root.glob("Sessions/*/agent.json"))
            self.assertEqual(len(paths), 1)
            config = json.loads(paths[0].read_text())
            token = (paths[0].parent / "client-token.txt").read_text()
            client = HttpsTransport(f'https://127.0.0.1:{config["Port"]}', token,
                                    str(paths[0].parent / "server-cert.pem"))
            context = ssl.create_default_context(cafile=str(paths[0].parent / "server-cert.pem"))
            client.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                                        urllib.request.HTTPSHandler(context=context))
            result = get_system_information(client, config["DeviceId"], allow_mock=True)
            self.assertTrue(result["mock"])
            if move_directory:
                paths[0].parent.rename(paths[0].parent.with_name("moved-session"))
            elif break_stop_marker:
                # A directory at STOP cannot be overwritten as a file, on either OS.
                Path(config["StopFile"]).mkdir()
            process.stdin.write("\n")
            process.stdin.flush()
            self.assertEqual(process.wait(timeout=10), 1 if break_stop_marker else 0)
            if not break_stop_marker:
                self.assertTrue(Path(config["StopFile"]).is_file())
            with self.assertRaises(WinFixError):
                get_system_information(client, config["DeviceId"], allow_mock=True)
            reader.join(timeout=5)
            self.assertNotIn(token, "".join(output))
            self.assertNotIn("Unhandled exception", "".join(output))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            reader.join(timeout=5)
            process.stdin.close()
            process.stdout.close()
