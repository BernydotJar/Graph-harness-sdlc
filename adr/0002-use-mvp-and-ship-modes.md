# 0002 Use MVP And SHIP Modes

Status: accepted

## Context

Not every feature needs the same production burden, but every feature needs controlled scope and verification.

## Decision

Support two modes:

- MVP: fast validated prototype or internal demo
- SHIP: shippable product increment with production-grade gates

## Consequences

- one harness supports different delivery speeds
- SHIP mode can reject features even when tests pass
- mode must be declared in `feature_list.json`

