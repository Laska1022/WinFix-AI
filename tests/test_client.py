import datetime as dt
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import http.client
import io
import os
import unittest
import uuid
from unittest.mock import Mock, patch
from tools.winfix_client import HttpsTransport, MAX_RESPONSE, NoRedirect, WinFixError, get_system_information, main


MARKER = b"SYNTHETIC_SERVER_PRIVATE_MARKER"
CHUNKED_HEADERS = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nTransfer-Encoding: chunked\r\n\r\n"
MALFORMED_RESPONSES = {
    "status": MARKER + b"\r\n\r\n",
    "header": b"HTTP/1.1 200 OK\r\nX-Detail: " + MARKER + b"x" * 65536 + b"\r\n\r\n",
    "chunk_size": CHUNKED_HEADERS + MARKER + b"\r\n",
    "truncated_chunk": CHUNKED_HEADERS + b"100\r\n" + MARKER,
}


class FakeTransport:
    def __init__(self, change=None):
        self.change = change or {}

    def post(self, payload):
        return {"schemaVersion": 1, "requestId": payload["requestId"], "deviceId": payload["deviceId"],
                "mock": False, "collectedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                "system": {"platform": "Windows", "computerName": "test", "osDescription": "test",
                           "osVersion": "test", "architecture": "X64", "timeZone": "UTC", "uptimeMilliseconds": 1},
                **self.change}


class ClientTests(unittest.TestCase):
    def protocol_opener(self, raw):
        # Use Python's actual HTTP parser without adding a certificate-generation
        # dependency to the cross-platform suite. TLS has separate integration tests.
        sock = Mock()
        sock.makefile.return_value = io.BytesIO(raw)
        response = http.client.HTTPResponse(sock)
        self.addCleanup(response.close)

        def open_response(*args, **kwargs):
            response.begin()
            return response

        opener = Mock()
        opener.open.side_effect = open_response
        return opener

    def test_transport_protocol_errors_are_safe(self):
        for name, raw in MALFORMED_RESPONSES.items():
            with self.subTest(response=name):
                client = HttpsTransport("https://localhost", "synthetic-credential")
                client.opener = self.protocol_opener(raw)
                with self.assertRaises(WinFixError) as raised:
                    client.post({})
                self.assertNotIn(MARKER.decode(), str(raised.exception))
                self.assertNotIn("synthetic-credential", str(raised.exception))
                self.assertTrue(raised.exception.__suppress_context__)

    def test_cli_protocol_errors_are_safe(self):
        argv = ["winfix_client.py", "get-system-information", "--endpoint", "https://localhost",
                "--device-id", str(uuid.uuid4())]
        for name, raw in MALFORMED_RESPONSES.items():
            with self.subTest(response=name):
                stdout, stderr = io.StringIO(), io.StringIO()
                with (patch("sys.argv", argv),
                      patch.dict(os.environ, WINFIX_TOKEN="synthetic-credential"),
                      patch("tools.winfix_client.urllib.request.build_opener", return_value=self.protocol_opener(raw)),
                      redirect_stdout(stdout), redirect_stderr(stderr)):
                    self.assertEqual(main(), 1)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(stderr.getvalue(),
                                 "WinFix request failed. Check credentials, identity, TLS, routing, response schema, and mock mode.\n")

    def test_transport_valid_http_response(self):
        client = HttpsTransport("https://localhost", "synthetic-credential")
        client.opener = self.protocol_opener(
            b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 11\r\n\r\n{"ok":true}')
        self.assertEqual(client.post({}), {"ok": True})

    def test_reject_insecure_or_ambiguous_origins(self):
        for origin in ("http://localhost", "https://user:pass@host", "https://host/path", "https://host?q=x", "https://host/#fragment"):
            with self.subTest(origin=origin), self.assertRaises(WinFixError):
                HttpsTransport(origin, "token")

    def test_reject_empty_or_header_injection_token(self):
        for token in ("", "x\r\nheader: value", "a b"):
            with self.assertRaises(WinFixError):
                HttpsTransport("https://localhost", token)

    def test_refuse_redirect(self):
        with self.assertRaises(WinFixError):
            NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.example")

    def test_identity_schema_and_evidence_validation(self):
        for change in ({"deviceId": "other"}, {"requestId": "other"}, {"schemaVersion": True},
                       {"schemaVersion": 2}, {"mock": True}, {"mock": "false"}, {"system": {}},
                       {"collectedAt": "2000-01-01T00:00:00+00:00"}, {"collectedAt": None}):
            with self.subTest(change=change), self.assertRaises(WinFixError):
                get_system_information(FakeTransport(change), str(uuid.uuid4()))

    def test_valid_response(self):
        result = get_system_information(FakeTransport(), str(uuid.uuid4()))
        self.assertEqual(result["system"]["platform"], "Windows")

    def test_transport_rejects_oversize_malformed_and_non_json(self):
        for body, content_type in ((b"x" * (MAX_RESPONSE + 1), "application/json"),
                                   (b"not json", "application/json"), (b"[]", "application/json"),
                                   (b"{}", "text/html")):
            client = HttpsTransport("https://localhost", "test")
            response = io.BytesIO(body)
            response.headers = Message()
            response.headers["Content-Type"] = content_type
            client.opener = Mock()
            client.opener.open.return_value = response
            with self.subTest(content_type=content_type, size=len(body)), self.assertRaises(WinFixError):
                client.post({})

    def test_transport_timeout_is_safe_error(self):
        client = HttpsTransport("https://localhost", "secret")
        client.opener = Mock()
        client.opener.open.side_effect = TimeoutError("secret")
        with self.assertRaises(WinFixError) as raised:
            client.post({})
        self.assertNotIn("secret", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
