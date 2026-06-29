# Release Readiness

SHIP mode should end with something that can be released or deliberately held.

## Checklist

- tests pass
- build passes when applicable
- no secrets exposed
- migrations reviewed when applicable
- environment variables documented
- observability hooks documented
- known debt documented
- release notes generated
- rollback or remediation note included
- review artifact exists
- human closure approval exists

## Release Notes

Release notes should include:

- feature id
- user-visible change
- operational notes
- migration notes
- known limitations
- rollback or remediation path

## Hold Criteria

Do not release when:

- production reviewer rejects the feature
- migrations are unapproved
- security issues are unresolved
- verification evidence is missing
- user-facing i18n/accessibility requirements are unmet

