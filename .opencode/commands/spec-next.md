# spec-next

MODE:
Select the feature mode from `feature_list.json`. Default to MVP only when the feature is explicitly marked MVP.

FEATURE:
Choose the first `pending` feature unless a human names a specific feature.

STATE:
Allowed start state: `pending`.
Allowed end state: `spec_ready`.

SOURCE OF TRUTH:
- `feature_list.json`
- `templates/feature/requirements.md`
- `templates/feature/design.md`
- `templates/feature/tasks.md`
- `docs/modes.md`
- `docs/production-readiness.md`

FILES YOU MAY READ:
- `feature_list.json`
- `docs/**`
- `templates/**`
- `progress/**`
- `specs/**`

FILES YOU MAY TOUCH:
- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `progress/current.md`
- `progress/history.md`

FILES YOU MUST NOT TOUCH:
- application source files
- dependency manifests
- lockfiles
- environment files
- existing specs for unrelated features

DO:
- Create requirements, design, and tasks for the selected feature.
- Include MVP criteria and SHIP criteria.
- Include i18n awareness for user-facing features.
- Include verification requirements.
- Move the feature to `spec_ready`.
- Run `./init.sh`.

DON'T:
- Implement application code.
- Approve the feature.
- Mark the feature `in_progress`, `review`, or `done`.
- Add dependencies.

OUTPUT:
- Feature id
- Mode
- Spec files created
- Validation result
- Approval request

STOP:
Stop after the spec is ready and ask for human approval.
