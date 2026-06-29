# Production Readiness Review Skill

Use this skill for SHIP mode reviews.

## Inputs

- active feature spec
- implementation diff
- verification evidence
- `docs/production-readiness.md`
- `docs/quality-gates.md`

## Output

- production review section or `progress/review_<feature-id>.md`

## Checklist

- security risks reviewed
- data correctness reviewed
- performance reviewed
- failure modes reviewed
- observability readiness reviewed
- test coverage reviewed
- UX/accessibility reviewed
- operations and release readiness reviewed

Reject closure when production evidence is missing.

