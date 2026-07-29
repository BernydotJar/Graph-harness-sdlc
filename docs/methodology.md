# Methodology

Graph Harness SDLC combines Spec-Driven Development, Harness Engineering, Loop Engineering and Executable Graph Engineering.

## Spec-Driven Development

The approved specification defines the implementation boundary before production work begins. Requirements, design, tasks, non-goals, file boundaries and verification commands must exist before execution.

## Harness Engineering

The harness makes correct work easier to perform and incorrect work harder to hide. It provides executable contracts, role separation, evidence capture, deterministic gates, checkpoints and repair behavior.

## Loop Engineering

Agents operate inside designed loops:

```text
context -> role -> ready node -> action -> evidence -> critique -> repair -> verification -> gate -> next state
```

A loop is useful only when it advances the graph or produces evidence that explains why progress cannot continue.

## Executable Graph Engineering

The execution graph is the source of truth for readiness, dependencies, revisions, gates and preserved evidence. Agents are interchangeable executors selected by capability.

## Principles

- One approved feature at a time unless the graph explicitly permits safe concurrency.
- Explicit, validated state transitions.
- Human approval before implementation where required.
- Producer, critic, fixer and verifier separation.
- Current-revision evidence before a gate can pass.
- Current documentation checkpoints for unstable external APIs.
- Production gates for software intended to ship.
- Localized repair instead of broad restart.
- Persistent checkpoints before long or risky operations.
- Program closure only through an explicit terminal outcome.

## Completion

The objective is not activity. The objective is to finish the declared product scope.

Execution continues until repository policy records one of:

- `COMPLETED`
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS`
- `SAFETY_STOP`

See [Program terminal states](terminal-states.md).
