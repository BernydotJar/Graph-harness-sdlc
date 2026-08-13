from __future__ import annotations

import json
import socket
import unittest
from datetime import UTC, datetime

from graph_harness.browser_cdp import (
    BrowserCdpClient,
    CdpProtocolError,
    CdpSession,
    CdpTarget,
    CdpTargetError,
    CdpTimeoutError,
    CdpUnavailableError,
    build_cdp_evidence,
    sanitize_cdp_evidence,
)


class FakeHttp:
    def __init__(self, routes: dict[str, bytes | str | BaseException]):
        self.routes = routes
        self.calls: list[tuple[str, float, dict[str, str]]] = []

    def __call__(self, url: str, timeout: float, headers: dict[str, str]):
        self.calls.append((url, timeout, dict(headers)))
        path = "/" + url.split("/", 3)[-1] if "/" in url.split("://", 1)[-1] else "/"
        value = self.routes[path]
        if isinstance(value, BaseException):
            raise value
        return value


class FakeSocket:
    def __init__(self, responses: list[str | bytes | BaseException]):
        self.responses = list(responses)
        self.sent: list[str] = []
        self.closed = False

    def send(self, payload: str) -> None:
        self.sent.append(payload)

    def recv(self) -> str | bytes:
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    def close(self) -> None:
        self.closed = True


class BrowserCdpTests(unittest.TestCase):
    def test_preflight_validates_discovery_and_host_override(self) -> None:
        http = FakeHttp(
            {
                "/json/version": json.dumps(
                    {
                        "Browser": "Chrome/151.0",
                        "Protocol-Version": "1.3",
                        "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/example",
                    }
                )
            }
        )
        client = BrowserCdpClient(
            "http://host.docker.internal:9222/",
            host_header="localhost:9222",
            http_get=http,
        )
        result = client.preflight()
        self.assertEqual("Chrome/151.0", result.browser)
        self.assertEqual("1.3", result.protocol_version)
        self.assertEqual("localhost:9222", http.calls[0][2]["Host"])

    def test_preflight_fails_closed_when_unavailable(self) -> None:
        client = BrowserCdpClient(
            "http://localhost:9222",
            http_get=FakeHttp({"/json/version": OSError("connection refused")}),
        )
        with self.assertRaises(CdpUnavailableError):
            client.preflight()

    def test_preflight_rejects_malformed_or_incomplete_payloads(self) -> None:
        malformed = BrowserCdpClient(
            "http://localhost:9222",
            http_get=FakeHttp({"/json/version": "not-json"}),
        )
        with self.assertRaises(CdpProtocolError):
            malformed.preflight()

        incomplete = BrowserCdpClient(
            "http://localhost:9222",
            http_get=FakeHttp({"/json/version": json.dumps({"Browser": "Chrome/151.0"})}),
        )
        with self.assertRaises(CdpProtocolError):
            incomplete.preflight()

    def test_target_listing_filters_to_pages_and_resolves_exact_or_regex(self) -> None:
        payload = [
            {
                "id": "page-1",
                "type": "page",
                "title": "Workflows - n8n",
                "url": "http://localhost:5678/home/workflows",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/page-1",
            },
            {
                "id": "worker-1",
                "type": "service_worker",
                "title": "worker",
                "url": "https://example.test/sw.js",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/worker-1",
            },
            {
                "id": "page-2",
                "type": "page",
                "title": "LCH Technologies | Google AI Studio",
                "url": "https://aistudio.google.com/apps/example",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/page-2",
            },
        ]
        http = FakeHttp({"/json/list": json.dumps(payload)})
        client = BrowserCdpClient(
            "http://localhost:9222",
            websocket_base_url="ws://bridge.internal:9222",
            http_get=http,
        )
        targets = client.list_targets()
        self.assertEqual(["page-1", "page-2"], [target.id for target in targets])
        self.assertEqual(
            "ws://bridge.internal:9222/devtools/page/page-1",
            targets[0].websocket_debugger_url,
        )
        self.assertEqual("page-1", client.resolve_target(title="Workflows - n8n").id)
        self.assertEqual("page-2", client.resolve_target(url=r"aistudio\.google\.com/apps/", regex=True).id)

    def test_target_resolution_rejects_ambiguous_matches(self) -> None:
        payload = [
            {
                "id": "a",
                "type": "page",
                "title": "Workflows - n8n",
                "url": "http://localhost:5678/home/workflows",
                "webSocketDebuggerUrl": "ws://localhost/a",
            },
            {
                "id": "b",
                "type": "page",
                "title": "Workflows - n8n",
                "url": "http://localhost:5678/home/workflows",
                "webSocketDebuggerUrl": "ws://localhost/b",
            },
        ]
        client = BrowserCdpClient(
            "http://localhost:9222",
            http_get=FakeHttp({"/json/list": json.dumps(payload)}),
        )
        with self.assertRaisesRegex(CdpTargetError, "ambiguous"):
            client.resolve_target(title="Workflows - n8n")

    def test_session_correlates_response_and_ignores_async_events(self) -> None:
        socket_ = FakeSocket(
            [
                json.dumps({"method": "Runtime.consoleAPICalled", "params": {}}),
                json.dumps({"id": 1, "result": {"result": {"value": 42}}}),
            ]
        )
        session = CdpSession(
            "ws://localhost:9222/devtools/page/one",
            websocket_factory=lambda _url, _timeout: socket_,
        )
        result = session.evaluate("6 * 7")
        self.assertEqual(42, result["result"]["value"])
        sent = json.loads(socket_.sent[0])
        self.assertEqual("Runtime.evaluate", sent["method"])
        self.assertTrue(sent["params"]["awaitPromise"])
        session.close()
        self.assertTrue(socket_.closed)

    def test_session_converts_timeout_and_protocol_error(self) -> None:
        timed_out = CdpSession(
            "ws://localhost/one",
            timeout=0.1,
            websocket_factory=lambda _url, _timeout: FakeSocket([socket.timeout("timed out")]),
        )
        with self.assertRaises(CdpTimeoutError):
            timed_out.call("Page.reload")

        rejected = CdpSession(
            "ws://localhost/two",
            websocket_factory=lambda _url, _timeout: FakeSocket(
                [json.dumps({"id": 1, "error": {"code": -32000, "message": "rejected"}})]
            ),
        )
        with self.assertRaises(CdpProtocolError):
            rejected.call("Page.reload")

    def test_evidence_sanitization_removes_configured_sensitive_keys(self) -> None:
        sanitized = sanitize_cdp_evidence(
            {
                "status": "PASS",
                "cookie": "sensitive-value",
                "Authorization": "sensitive-value",
                "nested": {
                    "access_token": "sensitive-value",
                    "password": "sensitive-value",
                    "safe": "ordinary-value",
                },
            }
        )
        self.assertEqual("PASS", sanitized["status"])
        self.assertNotIn("cookie", sanitized)
        self.assertNotIn("Authorization", sanitized)
        self.assertNotIn("access_token", sanitized["nested"])
        self.assertNotIn("password", sanitized["nested"])
        self.assertEqual("ordinary-value", sanitized["nested"]["safe"])

    def test_built_evidence_drops_query_fragment_userinfo_and_sensitive_metadata(self) -> None:
        target = CdpTarget(
            id="page-1",
            type="page",
            title="LCH",
            url="https://user:pass@example.com/path/to/app?state=opaque#fragment",
            websocket_debugger_url="ws://localhost:9222/devtools/page/page-1",
        )
        evidence = build_cdp_evidence(
            target,
            action="reload",
            result="PASS",
            metadata={"password": "sensitive-value", "http_status": 200},
            occurred_at=datetime(2026, 8, 13, 15, 0, tzinfo=UTC),
        )
        self.assertEqual("https://example.com/path/to/app", evidence["target"]["url"])
        self.assertEqual(200, evidence["metadata"]["http_status"])
        self.assertNotIn("password", evidence["metadata"])
        self.assertEqual("2026-08-13T15:00:00Z", evidence["occurred_at"])


if __name__ == "__main__":
    unittest.main()
