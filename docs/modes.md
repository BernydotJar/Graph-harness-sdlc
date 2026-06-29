# Modes

Every feature must declare a mode in `feature_list.json`.

## MVP Mode

Use MVP mode for fast validated prototypes and internal demos.

Required:

- requirements
- design
- tasks
- bounded scope
- basic test plan
- verification command
- review
- clear known gaps

Allowed:

- lightweight production criteria
- documented technical debt
- limited observability planning

Not allowed:

- random scope expansion
- unreviewed dependencies
- missing verification
- silent assumptions

## SHIP Mode

Use SHIP mode for shippable product increments.

Required:

- MVP criteria
- security analysis
- data correctness analysis
- performance analysis
- failure mode handling
- observability readiness
- comprehensive tests
- UX/accessibility checks
- operational constraints
- release or review artifact

SHIP mode can reject a feature even when tests pass.

