# Database Change Policy

Database changes are high-risk and require explicit approval.

## Default Rule

No schema changes, migrations, seed changes, database pushes, or destructive database commands without explicit human approval.

## Schema Changes

Specs must include:

- exact schema files touched
- new, changed, or removed fields
- nullability and default behavior
- relationship changes
- indexes and constraints
- read/write behavior changes
- migration and rollback plan

## Migrations

SHIP mode requires migration review before execution.

Checklist:

- migration is generated from reviewed schema changes
- data backfill behavior is documented
- rollback or remediation path is documented
- production timing constraints are known
- command is approved by a human

## Seeds

Seed changes must be deterministic and environment-aware.

Do not seed production-like data unless explicitly approved.

## Forbidden Without Approval

- `db push`
- `migrate deploy`
- `migrate reset`
- destructive SQL
- bulk updates
- production data exports
- credential or connection-string changes

