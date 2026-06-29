# Claude Operating Guide

Read `AGENTS.md`, then `RTK.md`, before taking action.

## Default Behavior

- Work from `feature_list.json`.
- Select only one feature at a time.
- Do not implement a feature unless its status is `approved`.
- Do not mark a feature `done` without reviewer approval and verification evidence.
- Respect file boundaries declared in command prompts and specs.

## Agent Routing

- Use the Leader role for orchestration.
- Use the Spec Author role for requirements, design, and tasks.
- Use the Implementer role only after human approval.
- Use the Reviewer role after implementation.
- Use the Production Reviewer role for SHIP mode.

## Stop Conditions

Stop and ask for human input when:

- The spec is missing or ambiguous.
- The requested change exceeds approved scope.
- A dependency, schema change, destructive command, or secret is required.
- More than one active feature is detected.
- Verification cannot run.

