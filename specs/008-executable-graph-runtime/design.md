# 008-executable-graph-runtime Design

## Approach

Implement the runtime as a dependency-free Python package owned by Graph Harness SDLC. Target repositories consume a pinned framework revision and provide only application-specific project projection and event files.

The runtime separates:

1. **Project definition** — immutable typed graph structure, dependencies, capabilities, file boundaries, and gate requirements.
2. **Event store** — append-only execution, approval, evidence, gate, failure, invalidation, repair, and checkpoint events.
3. **Projection** — derived node status, revision, active evidence, gate results, ready nodes, and repair plans.
4. **Commands** — validation, status, ready-node selection, approval, evidence, gate evaluation, transition, localized failure repair, and checkpoint recording.

Evidence is retained across repairs. A `node.invalidated` event increments the node revision, so previous evidence remains auditable but cannot satisfy current gates.

## Files You May Read

- `AGENTS.md`
- `RTK.md`
- `README.md`
- `feature_list.json`
- `docs/**`
- `templates/**`
- `specs/008-executable-graph-runtime/**`
- `progress/**`

## Files You May Touch

- `graph_harness/**`
- `schemas/**`
- `tests/**`
- `pyproject.toml`
- `README.md`
- `RTK.md`
- `docs/graph-engineering.md`
- `docs/verification.md`
- `docs/quality-gates.md`
- `feature_list.json`
- `init.sh`
- `progress/**`
- `specs/008-executable-graph-runtime/**`

## Files You Must Not Touch

- Product application repositories from this framework branch.
- External infrastructure.
- Secrets or credentials.
- Existing product-memory artifacts unrelated to runtime behavior.

## Data Contracts

### Project

`graph-harness.project.v1` contains:

- `project_id`
- `mode`: `MVP` or `SHIP`
- `gate_definitions[]`
- `nodes[]` with typed status, dependencies, capability, target-status gates, allowed paths, and metadata

### Event

`graph-harness.event.v1` contains:

- UUID event identity
- contiguous sequence
- UTC timestamp
- project identity
- typed event name
- optional node identity and current revision
- actor
- payload
- previous event hash
- event hash

### Derived State

`graph-harness.state.v1` is generated and never treated as an independent source of truth.

## Dependencies

No runtime dependency is added. Python 3.11+ standard library is sufficient. Packaging uses setuptools only when building a wheel; source execution requires no installation.

## Context7 Checkpoints

None. The implementation uses Python standard-library APIs with stable contracts and no external framework integration.

## Risks

- **Concurrent append corruption:** mitigated with an exclusive file lock, contiguous sequence validation, hash-chain validation, fsync, and optional expected-last-event optimistic concurrency.
- **Evidence reuse after failure:** mitigated by node revision binding and active-revision gate checks.
- **Broad repair:** mitigated by descendant traversal from the failed node and explicit preserved-node recording.
- **Competing sources of truth:** target repositories must generate project definitions from their existing canonical ledgers rather than copy them manually.
- **False production authority:** runtime gates prove configured evidence contracts only; they do not authorize release or external effects.

## Verification Plan

- `python3 -m unittest discover -s tests -v`
- `python3 -m compileall -q graph_harness`
- `python3 -m graph_harness --help`
- `./init.sh`
- `git diff --check`
- application-side pinned-consumer verification in the dependent PR
