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
- skills exist
- quality gate docs include all required gates
- example feature list JSON is valid

Feature specs must define additional verification commands before implementation starts.

Verification results should be recorded in `progress/current.md` or review artifacts when relevant.


## Runtime Verification

`./init.sh` also runs:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q graph_harness
```

A consuming repository must additionally execute the pinned runtime against its generated project contract and persistent event ledger. A valid JSON parse alone is insufficient: the runtime verifies dependency acyclicity, event hash continuity, node revisions, transition legality, evidence freshness, and gate references.
