# 0001 Use SDD Lifecycle

Status: accepted

## Context

Agentic delivery fails when implementation begins before the desired behavior, boundaries, and verification plan are explicit.

## Decision

Use the lifecycle:

`pending -> spec_ready -> approved -> in_progress -> review -> done`

Also support `blocked`.

## Consequences

- features are reviewed against specs, not vibes
- implementation waits for human approval
- status transitions are auditable

