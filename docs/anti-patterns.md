# Anti-Patterns

Avoid these failure modes.

## Implementing Before Spec

Code without requirements/design/tasks makes review subjective.

Fix:

- run `/spec-next`
- stop for approval

## Implementer Approves Itself

The implementer cannot validate its own work as done.

Fix:

- route to Reviewer
- close only after review and human approval

## Reading The Whole Repo Every Time

Large context hides relevant details and wastes tokens.

Fix:

- start from the active spec
- read targeted files only

## Hiding Blockers

Continuing through uncertainty creates silent defects.

Fix:

- record the blocker
- ask for the missing decision

## Tests Pass But Production Criteria Fail

SHIP mode requires more than tests.

Fix:

- apply production-readiness gates

## Casual Dependencies

Dependencies add attack surface and maintenance burden.

Fix:

- require explicit approval and document purpose

## Schema Drift During Implementation

Schema changes change production risk.

Fix:

- pause
- request schema approval
- apply database policy

## Marking Done After Build Only

Build success is not closure.

Fix:

- require review artifact, verification evidence, and closure approval

## Mixing Feature Scope

Combining unrelated feature work makes rollback and review harder.

Fix:

- split features
- keep one active feature

