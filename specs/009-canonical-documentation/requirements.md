# Requirements — 009 Canonical Multilingual Documentation

## Objective

Align the public documentation of Graph Harness SDLC with the canonical product definition supplied by the project owner.

## Functional requirements

1. `README.md` must be canonical English documentation.
2. The README must state the core principle: the execution graph is the source of truth and agents are interchangeable executors.
3. The README must define the execution lifecycle from ready node through persistent evidence and the next ready node.
4. The README must state that delivery continues until one of three program terminal states is reached:
   - `COMPLETED`
   - `PARTIAL_WITH_DOCUMENTED_BLOCKERS`
   - `SAFETY_STOP`
5. Spanish, Portuguese and Italian translations must exist and link back to the canonical English README.
6. A documentation landing page must expose:
   - Concepts
   - Runtime architecture
   - System architecture
   - Tutorials
   - Examples
   - Reference
7. Program terminal states must be documented separately from node lifecycle statuses.
8. Existing runtime contracts and source code must remain unchanged.
9. Documentation terminology must be reusable across consuming repositories and must avoid application-specific assumptions.

## Non-goals

- Changing runtime behavior.
- Adding new node statuses or event types.
- Changing JSON schemas.
- Creating a hosted documentation site.
- Translating every deep technical document in this feature.

## Acceptance criteria

- All required documentation files exist and internal links resolve.
- English is clearly identified as canonical.
- All four README variants express the same product model.
- Terminal-state semantics are explicit and do not conflict with node statuses.
- `./init.sh` passes.
- Unit tests and compile checks pass.
- A reviewer artifact records scope, consistency and link verification.
