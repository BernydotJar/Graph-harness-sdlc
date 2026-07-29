# Review — 008-executable-graph-runtime

## Decision

`PASS_WITH_DEPENDENT_ADOPTION_PENDING`

The framework runtime satisfies its bounded implementation contract and is suitable for pinned consumption by an application repository. The feature remains in `review` until application adoption proves the cross-repository contract and a human authorizes closure.

## Requirements Review

- Typed project, node, gate, event, and state contracts: PASS.
- Dependency cycle rejection and ready-node selection: PASS.
- Explicit approval and legal lifecycle transitions: PASS.
- Append-only persistent evidence with hash-chain integrity: PASS.
- Revision-scoped gate evidence: PASS.
- Localized repair preserving unrelated nodes and historical evidence: PASS.
- Optimistic writer protection: PASS.
- No application framework or external service dependency: PASS.

## Security and Data Correctness

- No secret collection, network egress, shell execution, database mutation, or external effect authority exists.
- Event appends use an exclusive lock, contiguous sequence, fsync, project binding, node revision binding, previous hash, and event hash.
- A modified event is rejected during projection.
- A stale writer can be rejected with `expected_last_event_id`.
- Gate PASS rejects missing required evidence kinds, failed evidence, unknown evidence, and evidence from a previous node revision.

## Failure and Repair Review

A failure event calculates descendants from the dependency graph. The source and applicable descendants receive `node.invalidated`, increment their revisions, and become `repair_required`. Unrelated nodes remain unchanged. Historical evidence is retained but no longer active for the new revision.

## Verification Evidence

```text
python3 -m unittest discover -s tests -v
6 tests PASS

python3 -m compileall -q graph_harness
PASS

./init.sh
Harness validation PASS; runtime tests PASS

python3 -m pip wheel . --no-deps --no-build-isolation
PASS

isolated venv install + graph-harness --help + imports
PASS

wheel SHA-256
a8ddf7fadeed0a68d30a5f30f08ddc561a5d2e3edbf88c1b6a9f4db61617f9fd
```

## Residual Risks

- Cross-repository consumption has not yet been proven on the application branch.
- File locking assumes a POSIX environment; Windows support is not claimed.
- The JSON schemas document contracts, while runtime validation remains the authoritative executable gate.
- Multi-event repair is durable event-by-event rather than a database transaction; partial execution remains detectable and resumable through the event chain.

## Required Before Done

1. Pin the framework commit in `AI-Native-Content-Agency-SaaS` without copying runtime modules.
2. Generate the application project contract from existing canonical ledgers.
3. Validate the application event ledger and graph state.
4. Pass the application production-readiness workflow at the exact head.
5. Obtain human close and merge approval.
