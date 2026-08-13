# 009 — Browser CDP Capability Design

## Architecture

Add `graph_harness/browser_cdp.py` as a domain adapter layer independent from the graph/event schemas.

### Core types

- `CdpPreflight`: normalized browser/protocol discovery result.
- `CdpTarget`: normalized page target.
- `BrowserCdpClient`: HTTP discovery and deterministic target resolution.
- `CdpSession`: one websocket target session with bounded request/response correlation.
- Typed error hierarchy for unavailable/protocol/target/timeout/dependency failures.

### HTTP discovery

`BrowserCdpClient` accepts:

- `endpoint`, e.g. `http://127.0.0.1:9222`;
- timeout;
- optional `Host` override for bridge/proxy scenarios;
- injectable HTTP getter for deterministic tests.

`preflight()` reads `/json/version`, validates `Browser`, `Protocol-Version`, and `webSocketDebuggerUrl`, and returns a typed result.

`list_targets()` reads `/json/list`, validates the response array, ignores non-page targets by default, and returns normalized targets with `webSocketDebuggerUrl`.

`resolve_target()` accepts exact or regex matching for URL/title and fails on zero or multiple matches.

### Websocket execution

The base package does not import a third-party websocket library at module import time. `CdpSession.connect()` lazily imports `websocket-client` when no injected websocket factory is supplied. The optional package extra is:

```toml
browser-cdp = ["websocket-client>=1.8,<2"]
```

The session correlates messages by numeric CDP request id, ignores asynchronous events while waiting, converts timeout-like exceptions into `CdpTimeoutError`, and surfaces CDP error payloads as `CdpProtocolError`.

Convenience methods build on generic `call()`:

- `evaluate(expression)`;
- `navigate(url)`;
- `reload(ignore_cache=False)`;
- `click(selector)`;
- `focus(selector)`.

Selectors and URLs are JSON-encoded into JavaScript expressions before evaluation.

### Evidence sanitization

`build_cdp_evidence()` persists only:

- timestamp;
- action/result;
- target id/title;
- target URL reduced to scheme + host + path;
- sanitized optional metadata.

Recursive sanitization removes keys whose normalized names match secret-bearing concepts such as cookie, password, authorization, private key, client secret, access token, refresh token, id token, local/session storage, and API key. String values are also redacted for bearer tokens, JWT-like values, and PEM private-key blocks.

No browser storage enumeration is part of this adapter.

## Backward compatibility

`NodeDefinition.capability` is already a free-form string, so no project/event schema change is required. Existing runtimes continue to work unchanged. Consumers opt into the adapter when a node declares `browser_cdp`.

## Operator bootstrap

macOS bootstrap is documented as an operator action, for example:

```bash
open -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --remote-allow-origins='*' \
  --user-data-dir="$HOME/.graph-harness-chrome-debug"
```

The adapter never executes this command automatically and never treats an authenticated browser profile as authority to bypass graph human/release gates.
