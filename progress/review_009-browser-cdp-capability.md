# Review — 009 Browser CDP Capability

Mode: SHIP
Result: PASS

## Producer

Implemented a reusable `browser_cdp` adapter with fail-closed Chrome discovery, deterministic page-target selection, bounded CDP execution, optional websocket support, bridge routing, and sanitized evidence. The graph and event schemas remain unchanged because `NodeDefinition.capability` is already free-form.

## Critic / Red Team

The first live run found a bridge defect: HTTP discovery succeeded with an overridden Host header, but the websocket connection did not carry the same bridge requirements and Chrome returned HTTP 500. The adapter was repaired to propagate `host_header` and to support an explicit `websocket_base_url`.

Target ambiguity is rejected rather than selecting arbitrarily. Evidence strips URL query, fragment, and user-info and omits configured sensitive field classes. Browser session state is not part of the evidence contract.

## Independent verification

- Unit tests: 15/15 PASS (9 CDP + 6 existing runtime).
- `python3 -m compileall -q graph_harness`: PASS.
- `./init.sh`: PASS.
- `git diff --check`: PASS.
- Clean wheel build/install/import: PASS.
- Optional `browser-cdp` extra install/import: PASS.
- Live Chrome preflight: Chrome 151 / CDP 1.3 PASS.
- Live AI Studio page target resolution + websocket + `Runtime.evaluate(document.title)`: PASS.
- Live sanitized evidence contains normalized target/action/result metadata only.

## Release gate

PASS for feature-branch publication. This does not authorize changes to external accounts, credentials, deployments, or other product release gates.
