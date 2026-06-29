# Verification

Run harness validation with:

```sh
./init.sh
```

`init.sh` validates:

- required harness files exist
- `feature_list.json` is valid JSON
- allowed statuses only
- at most one active feature among `approved`, `in_progress`, and `review`
- spec files exist for `spec_ready`, `approved`, `in_progress`, `review`, and `done` features
- command files exist
- command headings exist
- Context7 policy exists
- progress files exist

Feature specs must define additional verification commands before implementation starts.

Verification results should be recorded in `progress/current.md` or review artifacts when relevant.

