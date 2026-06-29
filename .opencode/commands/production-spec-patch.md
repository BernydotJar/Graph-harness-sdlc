# production-spec-patch

MODE:
SHIP only.

FEATURE:
Use the feature named by the human or the active SHIP feature.

STATE:
Allowed start state: `spec_ready` or `approved`.
Allowed end state: unchanged unless human approval is needed again.

SOURCE OF TRUTH:
- `feature_list.json`
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `docs/production-readiness.md`
- `docs/modes.md`

FILES YOU MAY READ:
- `feature_list.json`
- `specs/<feature-id>/**`
- `docs/**`
- `progress/**`

FILES YOU MAY TOUCH:
- `specs/<feature-id>/requirements.md`
- `specs/<feature-id>/design.md`
- `specs/<feature-id>/tasks.md`
- `progress/current.md`
- `progress/history.md`

FILES YOU MUST NOT TOUCH:
- application source files
- dependency manifests
- lockfiles
- specs for unrelated features

DO:
- Patch the spec to include SHIP mode criteria.
- Cover security, data correctness, performance, failure modes, observability, testing, UX/accessibility, and operations.
- Note any approval-impacting scope change.
- Run `./init.sh`.

DON'T:
- Implement code.
- Hide production risks.
- Approve your own changes.

OUTPUT:
- Feature id
- Production gaps found
- Spec patches made
- Approval impact
- Validation result

STOP:
Stop if the patch changes scope and ask for renewed human approval.
