# Security Review Skill

Use this skill when a feature touches auth, user input, private data, secrets, dependencies, or external services.

## Inputs

- active feature spec
- implementation diff
- `docs/security-model.md`

## Checklist

- input validation exists at trust boundaries
- authorization boundaries are explicit
- private data exposure is minimized
- errors are safe
- secrets are not logged or exposed
- dependencies are approved
- destructive operations have human approval

