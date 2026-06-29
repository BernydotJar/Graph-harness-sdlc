# approve-feature

MODE:
Use the mode already declared in `feature_list.json`.

FEATURE:
Use the feature named by the human.

STATE:
Allowed start state: `spec_ready`.
Allowed end state: `approved`.

SOURCE OF TRUTH:
- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `progress/current.md`

FILES YOU MAY READ:
- `feature_list.json`
- `specs/<feature-id>/**`
- `progress/**`

FILES YOU MAY TOUCH:
- `feature_list.json`
- `progress/current.md`
- `progress/history.md`

FILES YOU MUST NOT TOUCH:
- application source files
- docs unrelated to the feature
- specs for unrelated features
- dependency manifests
- lockfiles

DO:
- Confirm human approval is explicit.
- Confirm no other feature is active.
- Move the feature to `approved`.
- Record approval in progress files.
- Run `./init.sh`.

DON'T:
- Treat vague interest as approval.
- Change spec content during approval.
- Start implementation.

OUTPUT:
- Feature id
- Approval evidence
- New state
- Validation result

STOP:
Stop after approval is recorded.
