# Quality Gates

Quality gates define when a feature may move to the next state.

## Spec Gate

Inputs:

- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`

Checks:

- requirements are testable
- non-goals are explicit
- file boundaries are declared
- verification commands are defined
- mode-specific criteria are included

Transition:

- `pending -> spec_ready`

Required artifact:

- complete feature spec

Failure behavior:

- keep feature `pending`
- record blocker or missing information

## Approval Gate

Inputs:

- complete spec
- explicit human approval

Checks:

- scope is understood
- risks are acceptable
- no active feature conflict exists

Transition:

- `spec_ready -> approved`

Required artifact:

- approval entry in `progress/history.md`

Failure behavior:

- keep feature `spec_ready`

## Implementation Gate

Inputs:

- approved spec
- allowed file boundaries

Checks:

- no unapproved dependencies
- no unapproved schema changes
- no out-of-scope edits
- required docs checkpoints completed

Transition:

- `approved -> ready -> running -> review`

Required artifact:

- implementation notes and verification evidence

Failure behavior:

- keep feature `running` or set `blocked`

## Review Gate

Inputs:

- implementation
- tests
- verification evidence
- spec

Checks:

- behavior matches requirements
- implementation follows design
- tests cover required cases
- i18n/accessibility checks pass when applicable

Transition:

- `review -> done` only through close workflow

Required artifact:

- `progress/review_<feature-id>.md`

Failure behavior:

- keep feature `review` with findings

## Production Gate

Inputs:

- SHIP mode feature
- production review artifact

Checks:

- security
- data correctness
- performance
- failure modes
- observability readiness
- tests
- UX/accessibility
- operations

Transition:

- reviewer may recommend closure

Required artifact:

- production review section or `templates/review/production-review.md`

Failure behavior:

- reject closure even when tests pass

## Close Gate

Inputs:

- passing review
- passing verification
- human closure approval

Checks:

- no unresolved blocking findings
- release notes or closure notes exist when required
- known debt is documented

Transition:

- `review -> done`

Required artifact:

- closure entry in `progress/history.md`

Failure behavior:

- keep feature `review` or set `blocked`


## Program Terminal Outcome

A passing close gate completes a node or feature. The whole program reaches a terminal outcome only after repository policy evaluates the declared objective across the full graph. The permitted outcomes are `COMPLETED`, `PARTIAL_WITH_DOCUMENTED_BLOCKERS` and `SAFETY_STOP`. See [Program terminal states](terminal-states.md).
