# Current Progress

## Active Feature

None.

## Completed Feature

`009-browser-cdp-capability` — `done` — SHIP mode.

## Closure Evidence

- Reusable `browser_cdp` adapter implemented without project/event schema changes.
- Typed fail-closed discovery/target/session errors.
- Deterministic exact/regex page selection with ambiguity rejection.
- Docker/proxy bridge support through `host_header` and `websocket_base_url`.
- Evidence sanitizer strips URL query/fragment/user-info and omits sensitive field classes.
- Base package remains dependency-free; websocket execution is an optional package extra.
- Live Chrome 151 / CDP 1.3 execution against Google AI Studio passed.

## Verification

```text
./init.sh: PASS
unit tests: 15/15 PASS
compileall: PASS
wheel build/install/import: PASS
optional websocket extra: PASS
live Chrome CDP preflight/evaluate: PASS
```

## Authority Boundary

The capability can operate an intentionally opened browser target, but browser access does not replace human/release gates and session state is not graph state.
