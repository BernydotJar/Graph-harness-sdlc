# review-feature

MODE:
Use the mode in `feature_list.json`.

FEATURE:
Use the single feature with status `review`.

STATE:
Allowed start state: `review`.
Allowed end state: `review`, `blocked`, or reviewer recommendation for `done`.

SOURCE OF TRUTH:
- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `docs/production-readiness.md`
- `docs/verification.md`

FILES YOU MAY READ:
- implementation files touched by the feature
- tests touched by the feature
- `feature_list.json`
- `docs/**`
- `specs/<feature-id>/**`
- `progress/**`

FILES YOU MAY TOUCH:
- `progress/review_<feature-id>.md`
- `progress/current.md`
- `progress/history.md`
- `feature_list.json` only to set `blocked` when review cannot proceed

FILES YOU MUST NOT TOUCH:
- production source files
- test source files
- dependency manifests
- lockfiles
- environment files

DO:
- Review implementation against the spec.
- Check tests and verification evidence.
- Check i18n requirements for user-facing features.
- Apply SHIP gates when mode is SHIP.
- Write a review report.

DON'T:
- Edit production code.
- Approve missing verification.
- Mark the feature `done` directly unless the close command is being executed with human approval.

OUTPUT:
- Findings ordered by severity
- Pass/fail recommendation
- Verification reviewed
- Required fixes

STOP:
Stop after writing the review report.
