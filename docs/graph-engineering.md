# Graph Engineering

Graph Harness SDLC represents delivery through two related graphs.

## Product knowledge graph

The product knowledge graph contains persistent product entities:

- Requirement
- Feature
- Component
- API
- Schema
- Decision
- Risk
- Test
- Evaluation
- Commit
- Pull Request

Recommended relationships:

```text
DEPENDS_ON
IMPLEMENTS
VERIFIED_BY
EVIDENCED_BY
BLOCKED_BY
SUPERSEDES
AFFECTS
REPAIRS
```

## Execution graph

The execution graph contains operational units:

- Task
- Agent
- Tool
- Capability
- Gate
- HumanApproval
- Artifact
- Failure
- Checkpoint

A node may execute when its dependencies are satisfied, its locks are free, its prerequisite gates pass and an executor has the required capability.

## State and events

Execution uses versioned contracts and derived state:

```text
graph-harness.project.v1 + graph-harness.event.v1 JSONL
  -> graph-harness.state.v1
  -> generated projections
```

Each event preserves sequence, actor, node revision and a SHA-256 chain. A failed gate increments the revision of affected nodes. Earlier evidence remains auditable but becomes stale for current gates.

Ledgers, reports and progress documents are projections. They must not compete as independent sources of truth.

## Localized repair

When a gate fails:

1. identify the failed node and defective evidence;
2. compute affected descendants;
3. invalidate only that subgraph;
4. increment the revision of every affected node;
5. record a repair plan;
6. rerun only the required work and gates;
7. preserve unaffected evidence and nodes.

This model reduces broad restarts, context loss and unnecessary rework.

## Program completion

Node completion is not program completion. The graph reaches a program terminal state only when repository policy evaluates the declared objective, all required nodes, current evidence, blockers and safety boundaries. See [Program terminal states](terminal-states.md).
