# use-context7

MODE:
Documentation checkpoint.

FEATURE:
Use the feature whose spec or implementation depends on external framework/API behavior.

STATE:
No state changes.

SOURCE OF TRUTH:
- `docs/mcp-context7-policy.md`
- active feature spec
- current external documentation from Context7 or approved equivalent

FILES YOU MAY READ:
- `docs/mcp-context7-policy.md`
- `feature_list.json`
- `specs/<feature-id>/**`
- files directly relevant to the external framework/API question

FILES YOU MAY TOUCH:
- `progress/current.md`
- `progress/history.md`
- active feature spec only when documenting a required checkpoint

FILES YOU MUST NOT TOUCH:
- implementation files unless this command is explicitly combined with an approved implementation task
- dependency manifests
- lockfiles
- unrelated specs

DO:
- Use Context7 or current docs for framework/API questions listed in the policy.
- Record the documentation checkpoint when it affects spec or implementation decisions.
- Note the library/API version when available.

DON'T:
- Use stale memory for unstable external APIs.
- Use Context7 for simple local bookkeeping.
- Add dependencies.

OUTPUT:
- Documentation source
- Version or date
- Decision impact
- Files updated, if any

STOP:
Stop after the documentation checkpoint is recorded or reported.
