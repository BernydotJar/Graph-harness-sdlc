# Runtime Architecture

The Graph Harness runtime is a reusable Python package with no application dependency. Consuming repositories provide domain state and evidence through versioned contracts.

## Inputs

### Project definition

`graph-harness.project.v1` defines:

- project identity and mode;
- node identifiers, kinds and initial statuses;
- dependency edges;
- required capabilities;
- allowed paths;
- gate definitions and target-state gate requirements.

### Event ledger

`graph-harness.event.v1` is an append-only JSONL ledger. Events record approvals, evidence, gate evaluations, transitions, failures, invalidations, repair plans and checkpoints.

The store verifies:

- contiguous sequence numbers;
- project identity;
- node revision;
- optimistic append expectations;
- SHA-256 chain integrity.

## Derived state

The runtime replays the ledger over the project definition to derive `graph-harness.state.v1`. Derived state includes current node status, revision, active evidence, active approvals, gate evaluations, checkpoints and repair plans.

Evidence from an earlier node revision remains auditable but cannot satisfy a current gate.

## Scheduling

A node becomes ready when:

1. it is approved;
2. all dependencies are `done`;
3. every required gate for `ready` passes;
4. an executor has the required capability;
5. repository-owned permissions allow execution.

The current CLI exposes deterministic readiness. A consuming scheduler may add concurrency, locks and capacity management without changing the graph contract.

## Localized repair

A failure event identifies a source node and gate. The runtime computes descendants, increments affected revisions, invalidates stale evidence and records a repair plan. Nodes outside the affected subgraph remain untouched.

## Authority boundary

The runtime governs graph state. It does not independently authorize:

- merge
- release
- deployment
- spending
- secret mutation
- destructive data operations
- external side effects

Those authorities belong to explicit human or consuming-repository gates.

## CLI entry points

```sh
python3 -m graph_harness --project project.json --events events.jsonl validate
python3 -m graph_harness --project project.json --events events.jsonl status --pretty
python3 -m graph_harness --project project.json --events events.jsonl ready --pretty
```

See [Reference](reference.md) for event-producing commands.
