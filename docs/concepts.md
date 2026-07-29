# Concepts

Graph Harness SDLC treats software delivery as a persistent, executable graph rather than a conversation transcript or a queue of loosely related prompts.

## Execution graph

The execution graph is the source of truth for work readiness and delivery state. Nodes describe units of work; edges describe dependency or evidence relationships.

A node is executable only when:

- its dependencies are satisfied;
- its required gates are passing;
- its file and capability boundaries allow execution;
- its evidence belongs to the current node revision;
- no lock, safety rule or human gate prevents execution.

## Typed state

State is represented by versioned contracts rather than free-form progress notes. The current runtime consumes:

- `graph-harness.project.v1`
- `graph-harness.event.v1`

and derives:

- `graph-harness.state.v1`

Progress documents and dashboards are projections of that state, not competing sources of truth.

## Interchangeable executors

Agents are executors selected for capability, not authorities that own truth. A producer, critic, fixer or verifier may be replaced between steps without changing the graph or invalidating preserved evidence.

## Evidence

Evidence is a persistent, hashed record that demonstrates a claim about the current node revision. Typical evidence kinds include:

- specification
- test result
- static analysis
- security review
- production review
- artifact checksum
- human approval

Code existence is not evidence of completion by itself.

## Gates

A gate is a deterministic decision rule over current evidence. Gates prevent a node from advancing when required evidence is absent, stale, failed or outside the approved scope.

## Localized repair

When a gate fails, the runtime invalidates the failed node and only the descendants that depend on it. Unaffected nodes and their evidence remain valid. This produces repair plans instead of broad restarts.

## Checkpoints

A checkpoint records a resumable point in a long-running program. It captures the graph position, evidence summary and repository revision needed to recover without reconstructing state from chat history.

## Node status versus program outcome

Node statuses represent operational progress. Program terminal states represent the outcome of the entire delivery program. They are deliberately separate; see [Terminal states](terminal-states.md).
