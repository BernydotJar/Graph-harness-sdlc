# implement-feature

MODE:
Use the mode in `feature_list.json`.

FEATURE:
Use the single feature with status `approved`.

STATE:
Allowed start state: `approved`.
Allowed end state: `in_progress` during work, then `review` when implementation and verification are complete.

SOURCE OF TRUTH:
- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `docs/conventions.md`
- `docs/verification.md`

FILES YOU MAY READ:
- files named by the approved spec
- `feature_list.json`
- `docs/**`
- `specs/<feature-id>/**`
- `progress/**`

FILES YOU MAY TOUCH:
- only files explicitly allowed by `specs/<feature-id>/design.md`
- tests explicitly required by `specs/<feature-id>/tasks.md`
- `progress/current.md`
- `progress/history.md`
- `feature_list.json`

FILES YOU MUST NOT TOUCH:
- unrelated source files
- unrelated specs
- dependency manifests unless explicitly approved
- schema files unless explicitly approved
- environment files
- secrets

DO:
- Move the feature to `in_progress` before editing implementation files.
- Implement only approved tasks.
- Use Context7 for external framework/API work when required.
- Run required verification.
- Move the feature to `review` only when implementation is complete.

DON'T:
- Expand scope.
- Add dependencies without explicit approval.
- Run destructive database or filesystem commands without explicit approval.
- Mark the feature `done`.

OUTPUT:
- Feature id
- Files changed
- Tasks completed
- Verification evidence
- Remaining risks

STOP:
Stop when the feature is ready for review.
