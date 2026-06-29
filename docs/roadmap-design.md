# Roadmap Design

The roadmap lives in `feature_list.json`.

## Adding Features

Add a feature when:

- it has a clear outcome
- it can be specified independently
- it has a mode
- it does not silently merge unrelated work

## Splitting Features

Split a feature when:

- it touches unrelated domains
- it requires separate approval gates
- it mixes app behavior with infrastructure
- it includes both MVP and hardening scope

## Hardening Features

Hardening work should be explicit.

Examples:

- security pass
- performance pass
- accessibility pass
- observability pass
- migration cleanup

## Numbering

Do not renumber existing features after they are referenced in specs, reviews, or history.

Insert new features with the next available id.

## Dependencies

Document dependencies in the feature summary or spec.

Do not start a dependent feature while its prerequisite is blocked.

## Blocked Features

Blocked features stay in the roadmap.

Record:

- blocker
- owner of next decision
- earliest valid next command

