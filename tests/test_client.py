import datetime as dt
from email.message import Message
import io
import unittest
import uuid
from unittest.mock import Mock
from tools.winfix_client import HttpsTransport, MAX_RESPONSE, NoRedirect, WinFixError, get_system_information


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
