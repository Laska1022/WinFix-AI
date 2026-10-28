#!/usr/bin/env python3
"""Read-only HTTPS client. Uses configured HTTP(S) proxies and verified TLS."""
import argparse
import datetime as dt
import http.client
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Protocol

MAX_RESPONSE = 65536


class WinFixError(Exception):
    """Safe to display; never embeds tokens, request headers, or server bodies."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise WinFixError("Redirect refused; check the configured agent endpoint")


class Transport(Protocol):
    def post(self, payload: dict) -> dict: ...


class HttpsTransport:
    def __init__(self, endpoint: str, token: str, ca_file=None, timeout=10):
        parsed = urllib.parse.urlsplit(endpoint)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.query or parsed.fragment
                or parsed.path not in ("", "/")):
            raise WinFixError("Endpoint must be an HTTPS origin without credentials, path, query, or fragment")
        if not token or any(c.isspace() for c in token):
            raise WinFixError("A nonempty bearer credential without whitespace is required")
        if not 0 < timeout <= 60:
            raise WinFixError("Timeout must be between zero and 60 seconds")
        self.url = endpoint.rstrip("/") + "/v1/diagnostics/system"
        self.token = token
        self.timeout = timeout
        context = ssl.create_default_context(cafile=ca_file)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))

    def post(self, payload):
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode(), method="POST",
                                         headers={"Authorization": "Bearer " + self.token,
                                                  "Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                if response.headers.get_content_type() != "application/json":
                    raise WinFixError("Agent returned a non-JSON response")
                raw = response.read(MAX_RESPONSE + 1)
        except urllib.error.HTTPError as exc:
            exc.close()
            raise WinFixError(f"Agent rejected the request (HTTP {exc.code})") from None
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
            raise WinFixError("Connection failed; check TLS trust, proxy routing, hostname, and agent availability") from None
        if len(raw) > MAX_RESPONSE:
            raise WinFixError("Agent response exceeded the size limit")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError, RecursionError):
            raise WinFixError("Agent returned invalid JSON") from None
        if not isinstance(data, dict):
            raise WinFixError("Agent returned an invalid response object")
        return data


def get_system_information(transport: Transport, device_id: str, *, allow_mock=False):
    try:
        uuid.UUID(device_id)
    except (ValueError, AttributeError):
        raise WinFixError("Device ID must be a UUID") from None
    request_id = str(uuid.uuid4())
    result = transport.post({"deviceId": device_id, "requestId": request_id,
                             "issuedAt": dt.datetime.now(dt.timezone.utc).isoformat()})
    if (type(result.get("schemaVersion")) is not int or result["schemaVersion"] != 1
            or result.get("deviceId") != device_id or result.get("requestId") != request_id):
        raise WinFixError("Agent identity, request correlation, or schema mismatch")
    if type(result.get("mock")) is not bool or (result["mock"] and not allow_mock):
        raise WinFixError("Real Windows evidence required; mock response refused")
    system = result.get("system")
    if (not isinstance(system, dict) or system.get("platform") != ("Mock" if result["mock"] else "Windows")
            or any(not isinstance(system.get(k), str) or not system[k] for k in
                   ("computerName", "osDescription", "osVersion", "architecture", "timeZone"))
            or type(system.get("uptimeMilliseconds")) is not int or system["uptimeMilliseconds"] < 0):
        raise WinFixError("Agent returned incomplete system information")
    try:
        collected = dt.datetime.fromisoformat(result["collectedAt"].replace("Z", "+00:00"))
        if abs((dt.datetime.now(dt.timezone.utc) - collected).total_seconds()) > 120:
            raise ValueError("stale")
    except (KeyError, ValueError, TypeError, AttributeError):
        raise WinFixError("Agent returned invalid or stale collection time") from None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["get-system-information"])
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--ca-file", help="Explicitly trusted certificate/CA PEM; never disables verification")
    parser.add_argument("--allow-mock", action="store_true", help="Local tests only; never Windows acceptance")
    args = parser.parse_args()
    try:
        transport = HttpsTransport(args.endpoint, os.environ.get("WINFIX_TOKEN", ""), args.ca_file)
        result = get_system_information(transport, args.device_id, allow_mock=args.allow_mock)
        print(json.dumps(result, indent=2))
    except WinFixError as error:
        # WinFixError messages are deliberately independent of server bodies/secrets.
        print(f"WinFix request failed: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError):
        # Details from arbitrary exceptions may contain server-controlled data or credentials.
        print("WinFix request failed. Check credentials, identity, TLS, routing, response schema, and mock mode.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
