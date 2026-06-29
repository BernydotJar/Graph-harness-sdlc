# close-feature

MODE:
Use the mode in `feature_list.json`.

FEATURE:
Use the feature named by the human or the reviewed feature.

STATE:
Allowed start state: `review`.
Allowed end state: `done`.

SOURCE OF TRUTH:
- `feature_list.json`
- `specs/<feature-id>/**`
- `progress/review_<feature-id>.md`
- `progress/current.md`
- `progress/history.md`

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
- tests
- docs unrelated to closure
- dependency manifests
- lockfiles

DO:
- Confirm review passed.
- Confirm required verification passed.
- Confirm human closure approval.
- Move the feature to `done`.
- Record closure evidence.
- Run `./init.sh`.

DON'T:
- Close a feature with unresolved blocking findings.
- Close without verification evidence.
- Edit implementation files.

OUTPUT:
- Feature id
- Closure evidence
- Verification evidence
- New state

STOP:
Stop after the feature is closed.
