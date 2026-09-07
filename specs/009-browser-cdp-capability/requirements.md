# 009 — Browser CDP Capability Requirements

Mode: SHIP
Status: approved by explicit human request in the LCH Website product-completion session.

## Goal
Provide a reusable `browser_cdp` capability for Graph Harness consumers that can preflight, select, inspect, and operate an intentionally opened Chrome instance through the Chrome DevTools Protocol without turning browser credentials into graph state or evidence.

## Functional requirements

1. A consuming node may declare `capability: "browser_cdp"` without changing `graph-harness.project.v1` schema compatibility.
2. The adapter must preflight a configured Chrome DevTools HTTP endpoint using `/json/version` and fail closed if unreachable, malformed, or missing required CDP metadata.
3. The adapter must list `/json/list` targets and select `type=page` targets by deterministic exact or regular-expression matching against URL/title.
4. Ambiguous target matches must fail rather than select arbitrarily.
5. A controlled CDP session must support:
   - generic protocol calls;
   - JavaScript evaluation;
   - navigation;
   - reload;
   - DOM click and focus helpers.
6. CDP websocket execution must use an optional dependency so the base Graph Harness runtime remains third-party-dependency free.
7. Evidence helpers must strip URL query/fragment data and redact or omit credential-bearing keys/values.
8. Browser storage, cookies, authorization headers, OAuth tokens, passwords, private keys, and credential API responses must never be persisted automatically.
9. macOS Chrome bootstrap must be documented as operator setup, not graph state.

## Failure semantics

- Unreachable HTTP endpoint -> `CdpUnavailableError`.
- Malformed/invalid discovery payload -> `CdpProtocolError`.
- Missing/ambiguous target -> `CdpTargetError`.
- Session timeout -> `CdpTimeoutError`.
- Missing optional websocket dependency -> `CdpDependencyError`.

## SHIP acceptance criteria

- Unit tests cover valid preflight, unavailable endpoint, malformed JSON, page filtering, regex/exact matching, ambiguous matches, websocket timeout, evidence URL sanitization, and secret redaction.
- Existing executable graph runtime tests remain green.
- Base installation remains dependency-free.
- Optional `browser-cdp` package extra is documented.
- README and RTK document the capability and security boundary.
- `./init.sh`, `python -m unittest`, and compile verification pass.
