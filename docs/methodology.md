# Methodology

`Graph-harness-sdlc` combines Spec-Driven Development and Loop Engineering.

Spec-Driven Development means the spec is the source of truth before implementation begins. Requirements, design, and tasks must exist before code changes.

Loop Engineering means the agent operates inside a designed loop:

- context
- role
- command
- file boundary
- action
- verification
- review
- state transition

The harness is not a prompt collection. It is an execution environment for controlled agentic delivery.

## Principles

- One feature at a time.
- Explicit status transitions.
- Human approval before implementation.
- Review before closure.
- Verification evidence before done.
- Current documentation for unstable external APIs.
- Production gates when software is intended to ship.

