# System Architecture

Graph Harness SDLC separates product knowledge, execution control, interchangeable executors and repository authority.

## Product knowledge graph

The product knowledge graph contains durable entities such as:

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

Useful relationships include:

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

The execution graph contains operational entities:

- Task
- Agent
- Tool
- Capability
- Gate
- HumanApproval
- Artifact
- Failure
- Checkpoint

The execution graph determines what may run next. The knowledge graph explains what the work means and how it relates to the product.

## Executor roles

The default lifecycle separates responsibilities:

- **Producer** creates the scoped implementation or artifact.
- **Critic / Red Team** searches for defects, contradictions and unhandled risks.
- **Fixer** repairs only verified findings within the approved boundary.
- **Independent Verifier** validates requirements and evidence without approving its own work.
- **Release Gate** applies repository and human authority before closure or external effects.

These are capabilities, not permanently assigned identities.

## Persistent control plane

```text
Canonical intent
      ↓
Versioned specification
      ↓
Executable graph + append-only events
      ↓
Derived typed state
      ↓
Executors and tools
      ↓
Evidence and deterministic gates
      ↓
Checkpoint or terminal outcome
```

## Consuming repositories

A consuming repository owns:

- product requirements;
- domain adapters;
- repository-specific quality gates;
- credentials and external-effect permissions;
- deployment and operational policy.

Graph Harness SDLC owns reusable execution semantics and must not absorb product-specific assumptions.
