from __future__ import annotations

import json
import re
import socket
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Mapping, Protocol
from urllib.error import URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


class CdpError(RuntimeError):
    """Base error for the browser CDP capability."""


class CdpUnavailableError(CdpError):
    """Raised when the configured CDP endpoint or websocket is unavailable."""


class CdpProtocolError(CdpError):
    """Raised when Chrome or a CDP target returns malformed or rejected data."""


class CdpTargetError(CdpError):
    """Raised when a requested browser target is missing or ambiguous."""


class CdpTimeoutError(CdpError):
    """Raised when a CDP request exceeds its bounded timeout."""


class CdpDependencyError(CdpError):
    """Raised when optional websocket execution support is not installed."""


@dataclass(frozen=True)
class CdpPreflight:
    browser: str
    protocol_version: str
    websocket_debugger_url: str


@dataclass(frozen=True)
class CdpTarget:
    id: str
    type: str
    title: str
    url: str
    websocket_debugger_url: str


class HttpGetter(Protocol):
    def __call__(self, url: str, timeout: float, headers: Mapping[str, str]) -> bytes | str: ...


class WebSocketLike(Protocol):
    def send(self, payload: str) -> Any: ...

    def recv(self) -> str | bytes: ...

    def close(self) -> Any: ...


WebSocketFactory = Callable[[str, float], WebSocketLike]


class BrowserCdpClient:
    """Fail-closed Chrome DevTools Protocol discovery and target selection."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout: float = 5.0,
        host_header: str | None = None,
        websocket_base_url: str | None = None,
        http_get: HttpGetter | None = None,
    ) -> None:
        endpoint = endpoint.strip().rstrip("/")
        if not endpoint:
            raise ValueError("CDP endpoint must be non-empty")
        if timeout <= 0:
            raise ValueError("CDP timeout must be positive")
        self.endpoint = endpoint
        self.timeout = float(timeout)
        self.host_header = host_header
        self.websocket_base_url = websocket_base_url.rstrip("/") if websocket_base_url else None
        self._http_get = http_get or self._default_http_get

    @staticmethod
    def _default_http_get(url: str, timeout: float, headers: Mapping[str, str]) -> bytes:
        request = Request(url, headers=dict(headers))
        with urlopen(request, timeout=timeout) as response:
            return response.read()

    def _get_json(self, path: str) -> Any:
        headers = {"Accept": "application/json"}
        if self.host_header:
            headers["Host"] = self.host_header
        try:
            raw = self._http_get(f"{self.endpoint}{path}", self.timeout, headers)
        except (TimeoutError, socket.timeout) as error:
            raise CdpTimeoutError(f"CDP HTTP request timed out for {path}") from error
        except (OSError, URLError) as error:
            raise CdpUnavailableError(f"CDP endpoint unavailable for {path}: {error}") from error
        if isinstance(raw, bytes):
            try:
                raw = raw.decode("utf-8")
            except UnicodeDecodeError as error:
                raise CdpProtocolError(f"CDP {path} is not valid UTF-8") from error
        try:
            return json.loads(raw)
        except (TypeError, json.JSONDecodeError) as error:
            raise CdpProtocolError(f"CDP {path} returned malformed JSON") from error

    def preflight(self) -> CdpPreflight:
        payload = self._get_json("/json/version")
        if not isinstance(payload, Mapping):
            raise CdpProtocolError("CDP /json/version root must be an object")
        browser = payload.get("Browser")
        protocol = payload.get("Protocol-Version")
        websocket_url = payload.get("webSocketDebuggerUrl")
        if not all(isinstance(value, str) and value.strip() for value in (browser, protocol, websocket_url)):
            raise CdpProtocolError(
                "CDP /json/version must include Browser, Protocol-Version, and webSocketDebuggerUrl"
            )
        return CdpPreflight(
            browser=browser.strip(),
            protocol_version=protocol.strip(),
            websocket_debugger_url=websocket_url.strip(),
        )

    def list_targets(self, *, include_non_pages: bool = False) -> list[CdpTarget]:
        payload = self._get_json("/json/list")
        if not isinstance(payload, list):
            raise CdpProtocolError("CDP /json/list root must be an array")
        targets: list[CdpTarget] = []
        for item in payload:
            if not isinstance(item, Mapping):
                continue
            target_type = item.get("type")
            if target_type != "page" and not include_non_pages:
                continue
            target_id = item.get("id")
            title = item.get("title", "")
            url = item.get("url", "")
            websocket_url = item.get("webSocketDebuggerUrl")
            if not (
                isinstance(target_id, str)
                and target_id
                and isinstance(target_type, str)
                and target_type
                and isinstance(title, str)
                and isinstance(url, str)
                and isinstance(websocket_url, str)
                and websocket_url
            ):
                continue
            targets.append(
                CdpTarget(
                    id=target_id,
                    type=target_type,
                    title=title,
                    url=url,
                    websocket_debugger_url=self._rewrite_websocket_url(websocket_url),
                )
            )
        return targets

    def _rewrite_websocket_url(self, discovered_url: str) -> str:
        if not self.websocket_base_url:
            return discovered_url
        base = urlsplit(self.websocket_base_url)
        discovered = urlsplit(discovered_url)
        if base.scheme not in {"ws", "wss"} or not base.netloc:
            raise CdpProtocolError("websocket_base_url must use ws:// or wss:// with a host")
        return urlunsplit((base.scheme, base.netloc, discovered.path, discovered.query, discovered.fragment))

    def resolve_target(
        self,
        *,
        url: str | None = None,
        title: str | None = None,
        regex: bool = False,
    ) -> CdpTarget:
        if url is None and title is None:
            raise ValueError("resolve_target requires url and/or title")

        def matches(value: str, pattern: str | None) -> bool:
            if pattern is None:
                return True
            if not regex:
                return value == pattern
            try:
                return re.search(pattern, value) is not None
            except re.error as error:
                raise CdpTargetError(f"invalid target regular expression: {error}") from error

        found = [
            target
            for target in self.list_targets()
            if matches(target.url, url) and matches(target.title, title)
        ]
        if not found:
            raise CdpTargetError("no CDP page target matched the requested URL/title")
        if len(found) > 1:
            ids = ", ".join(sorted(target.id for target in found))
            raise CdpTargetError(f"ambiguous CDP target match: {ids}")
        return found[0]

    def open_session(
        self,
        target: CdpTarget,
        *,
        websocket_factory: WebSocketFactory | None = None,
    ) -> "CdpSession":
        return CdpSession(
            target.websocket_debugger_url,
            timeout=self.timeout,
            host_header=self.host_header,
            websocket_factory=websocket_factory,
        )


class CdpSession:
    """Bounded request/response CDP websocket session."""

    def __init__(
        self,
        websocket_url: str,
        *,
        timeout: float = 5.0,
        host_header: str | None = None,
        websocket_factory: WebSocketFactory | None = None,
    ) -> None:
        if not websocket_url.strip():
            raise ValueError("CDP websocket URL must be non-empty")
        if timeout <= 0:
            raise ValueError("CDP timeout must be positive")
        self.websocket_url = websocket_url
        self.timeout = float(timeout)
        self.host_header = host_header
        self._factory = websocket_factory
        self._socket: WebSocketLike | None = None
        self._next_id = 0

    def connect(self) -> "CdpSession":
        if self._socket is not None:
            return self
        factory = self._factory
        if factory is None:
            try:
                import websocket  # type: ignore[import-not-found]
            except ImportError as error:
                raise CdpDependencyError(
                    "CDP websocket execution requires the optional 'browser-cdp' package extra"
                ) from error

            def factory(url: str, timeout: float) -> WebSocketLike:
                options: dict[str, Any] = {"timeout": timeout, "suppress_origin": True}
                if self.host_header:
                    options["host"] = self.host_header
                return websocket.create_connection(url, **options)

        try:
            self._socket = factory(self.websocket_url, self.timeout)
        except Exception as error:  # dependency-specific exception hierarchy is optional
            if _looks_like_timeout(error):
                raise CdpTimeoutError("CDP websocket connection timed out") from error
            raise CdpUnavailableError(f"CDP websocket connection failed: {error}") from error
        return self

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def __enter__(self) -> "CdpSession":
        return self.connect()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def call(self, method: str, params: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        if not method.strip():
            raise ValueError("CDP method must be non-empty")
        self.connect()
        assert self._socket is not None
        self._next_id += 1
        request_id = self._next_id
        request = {"id": request_id, "method": method, "params": dict(params or {})}
        try:
            self._socket.send(json.dumps(request, separators=(",", ":")))
        except Exception as error:
            if _looks_like_timeout(error):
                raise CdpTimeoutError(f"CDP send timed out for {method}") from error
            raise CdpUnavailableError(f"CDP send failed for {method}: {error}") from error

        deadline = time.monotonic() + self.timeout
        while True:
            if time.monotonic() >= deadline:
                raise CdpTimeoutError(f"CDP request timed out for {method}")
            try:
                raw = self._socket.recv()
            except Exception as error:
                if _looks_like_timeout(error):
                    raise CdpTimeoutError(f"CDP request timed out for {method}") from error
                raise CdpUnavailableError(f"CDP receive failed for {method}: {error}") from error
            if isinstance(raw, bytes):
                try:
                    raw = raw.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise CdpProtocolError("CDP websocket returned non-UTF-8 data") from error
            try:
                response = json.loads(raw)
            except (TypeError, json.JSONDecodeError) as error:
                raise CdpProtocolError("CDP websocket returned malformed JSON") from error
            if not isinstance(response, Mapping):
                raise CdpProtocolError("CDP websocket response must be an object")
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise CdpProtocolError(f"CDP {method} failed: {response['error']}")
            result = response.get("result", {})
            if not isinstance(result, Mapping):
                raise CdpProtocolError(f"CDP {method} result must be an object")
            return result

    def evaluate(self, expression: str) -> Mapping[str, Any]:
        return self.call(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": True, "returnByValue": True},
        )

    def navigate(self, url: str) -> Mapping[str, Any]:
        return self.call("Page.navigate", {"url": url})

    def reload(self, *, ignore_cache: bool = False) -> Mapping[str, Any]:
        return self.call("Page.reload", {"ignoreCache": bool(ignore_cache)})

    def click(self, selector: str) -> Mapping[str, Any]:
        encoded = json.dumps(selector)
        return self.evaluate(
            "(()=>{const e=document.querySelector(" + encoded + ");"
            "if(!e)return {ok:false,reason:'not-found'};e.click();return {ok:true};})()"
        )

    def focus(self, selector: str) -> Mapping[str, Any]:
        encoded = json.dumps(selector)
        return self.evaluate(
            "(()=>{const e=document.querySelector(" + encoded + ");"
            "if(!e)return {ok:false,reason:'not-found'};e.focus();return {ok:true};})()"
        )


_SENSITIVE_KEY_FRAGMENTS = (
    "cookie",
    "authorization",
    "password",
    "passwd",
    "secret",
    "privatekey",
    "accesstoken",
    "refreshtoken",
    "idtoken",
    "apikey",
    "localstorage",
    "sessionstorage",
    "credential",
)
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\b")


def _normalize_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _sensitive_key(value: str) -> bool:
    normalized = _normalize_key(value)
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _sanitize_string(value: str) -> str:
    if "PRIVATE KEY" in value.upper():
        return "[REDACTED]"
    value = _BEARER_RE.sub("Bearer [REDACTED]", value)
    value = _JWT_RE.sub("[REDACTED_JWT]", value)
    return value


def sanitize_cdp_evidence(value: Any) -> Any:
    """Recursively remove secret-bearing keys and redact common token material."""

    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _sensitive_key(key_text):
                continue
            sanitized[key_text] = sanitize_cdp_evidence(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_cdp_evidence(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_cdp_evidence(item) for item in value]
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def sanitize_target_url(url: str) -> str:
    """Drop query, fragment, and user info before persisting a browser target URL."""

    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme, host, path, "", ""))


def build_cdp_evidence(
    target: CdpTarget,
    *,
    action: str,
    result: str,
    metadata: Mapping[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a graph-safe evidence payload without browser credential material."""

    when = occurred_at or datetime.now(UTC)
    payload: dict[str, Any] = {
        "occurred_at": when.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "action": action,
        "result": result,
        "target": {
            "id": target.id,
            "title": target.title,
            "url": sanitize_target_url(target.url),
        },
    }
    if metadata:
        payload["metadata"] = sanitize_cdp_evidence(metadata)
    return sanitize_cdp_evidence(payload)


def _looks_like_timeout(error: BaseException) -> bool:
    return isinstance(error, (TimeoutError, socket.timeout)) or "timeout" in type(error).__name__.lower()
