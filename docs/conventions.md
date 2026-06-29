# Conventions

## Naming

- Feature ids use a three-digit prefix and kebab-case title.
- Specs live in `specs/<feature-id>/`.
- Review reports use `progress/review_<feature-id>.md`.

## Status Changes

- Change status only through the lifecycle.
- Do not skip approval.
- Do not mark `done` without review and verification evidence.

## Dependencies

Do not add dependencies without explicit approval.

## Schema And Data

Do not change schemas, migrations, or database state without explicit approval.

## i18n

For user-facing features, specs and reviews must check:

- English copy
- Spanish copy
- layout resilience for both languages
- validation and error messages
- empty states
- accessibility labels

