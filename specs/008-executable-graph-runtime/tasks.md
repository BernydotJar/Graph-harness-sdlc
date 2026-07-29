# 008-executable-graph-runtime Tasks

## Implementation Tasks

- [x] Define typed node, gate, event, and project contracts.
- [x] Implement append-only event storage with locking, optimistic concurrency, sequence validation, and SHA-256 hash chaining.
- [x] Implement graph projection, dependency readiness, lifecycle transition enforcement, evidence freshness, and gate enforcement.
- [x] Implement localized repair with descendant invalidation and revision-scoped evidence.
- [x] Implement CLI commands for validation, status, readiness, approval, evidence, gates, transitions, failures, and checkpoints.
- [x] Add project and event JSON schemas.
- [x] Add package metadata and source execution entrypoint.
- [x] Add tests for positive and fail-closed behavior.
- [ ] Integrate the pinned runtime into `AI-Native-Content-Agency-SaaS` without copying framework internals.

## Verification Tasks

- [x] Run `python3 -m unittest discover -s tests -v`.
- [x] Run `python3 -m compileall -q graph_harness`.
- [x] Run `python3 -m graph_harness --help`.
- [ ] Run the updated `./init.sh`.
- [ ] Run application graph-adapter verification.
- [ ] Record exact commit and CI evidence.

## Review Tasks

- [ ] Review requirements coverage.
- [ ] Review event integrity and transition invariants.
- [ ] Review localized repair preservation behavior.
- [ ] Review application adapter for source-of-truth duplication.
- [ ] Apply SHIP production gates.

## Stop Conditions

- A target repository must copy framework runtime code instead of pinning it.
- A transition would bypass human approval or configured gates.
- A repair would invalidate unrelated nodes or delete historical evidence.
- A release, deployment, protected-branch merge, spend, secret mutation, or external effect is required.
