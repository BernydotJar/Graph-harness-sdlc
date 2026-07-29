# 008-executable-graph-runtime Requirements

## Summary

Provide a reusable, executable Graph Harness SDLC runtime so application repositories can execute a typed dependency graph, persist tamper-evident evidence, enforce lifecycle and production gates, and repair only the affected subgraph after a failure.

## Mode

SHIP.

## Human Approval

The user explicitly directed this session to use Graph Harness SDLC as the execution runtime for `AI-Native-Content-Agency-SaaS`, to reuse framework concepts rather than duplicate them, and to require valid graph state plus gate-satisfying evidence for every completed feature. That directive authorizes this bounded runtime feature and its application adapter. It does not authorize release, deployment, protected-branch merge, external infrastructure, spending, or external effects.

## Acceptance Criteria

- [x] A standard-library Python package exposes a CLI and importable runtime.
- [x] Project definitions use a versioned typed JSON contract with validated node states, dependencies, capabilities, path boundaries, and gate requirements.
- [x] Runtime events use a versioned append-only JSONL contract with contiguous sequence numbers and a verified SHA-256 hash chain.
- [x] Invalid state transitions, dependency cycles, missing approvals, missing evidence, stale evidence, and failed gates are rejected.
- [x] Ready-node selection requires completed dependencies and applicable gates.
- [x] Localized repair records a failure, invalidates only the source node and descendants, increments node revisions, and preserves unaffected evidence.
- [x] Optimistic append protection rejects a stale writer.
- [x] JSON schemas document project and event contracts.
- [x] Unit tests cover lifecycle, gates, tamper detection, dependency readiness, localized repair, cycle rejection, and concurrent-writer protection.
- [ ] Application adoption is verified against a pinned framework commit in a separate repository change.

## Non-Goals

- No dashboard, hosted service, database, queue, model provider, or agent vendor integration.
- No duplication of application-specific task ledgers, specs, or product evidence inside the framework.
- No autonomous merge, release, deployment, spending, secret mutation, or external effect authority.
- No replacement of a target repository's domain-specific validators.

## i18n

- CLI machine output is stable JSON.
- Human-facing errors are concise English developer messages.
- No UI copy or layout is introduced.

## SHIP Criteria

- **Security:** event integrity is hash-chained; file writes are append-only under an exclusive lock; no shell execution or secret collection exists in the runtime.
- **Data correctness:** schemas are versioned; sequence, project identity, node revision, dependency acyclicity, transition legality, evidence freshness, and gate references are validated fail-closed.
- **Performance:** projection is linear in events plus graph edges; localized repair traverses only descendants.
- **Failure modes:** malformed JSON, broken hashes, stale writers, unknown nodes/gates, cycles, invalid transitions, missing approval, and stale evidence fail with non-zero status.
- **Observability readiness:** CLI returns deterministic JSON summaries; checkpoints and repair plans are persistent events.
- **Testing:** standard-library unit tests exercise positive and negative paths.
- **UX/accessibility:** not applicable to the headless runtime; output remains scriptable and readable.
- **Operations:** no dependency installation is required to execute the runtime; application release and external operations remain separately gated.
