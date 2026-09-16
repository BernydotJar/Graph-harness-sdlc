# 009 — Tasks

## Approved scope

The user explicitly approved implementation of the Foundation-inspired Graph Harness extensions on 2026-09-15/16, with one architectural constraint: UiPath/RPA must remain optional and must not become the center of the framework.

## Implementation tasks

- [x] GH-F1: implement versioned policy model and hierarchical resolver.
- [x] GH-F2: implement provider-neutral pre-action enforcement with allow/warn/deny.
- [x] GH-F3: implement provider adapter contract and Claude/Codex/Gemini built-ins.
- [x] GH-F4: implement generic preflight and non-destructive bootstrap with dry-run.
- [x] GH-F5: implement read-only doctor and provider projection drift manifest.
- [x] GH-F6: implement lowest-precedence developer preference profiles.
- [x] GH-F7: implement stable/experimental skill registry and catalog validation.
- [x] GH-F8: implement local provider-neutral attribution metadata.
- [x] Extend CLI without breaking existing runtime command syntax.
- [x] Add architecture documentation explicitly making deterministic workflows optional.
- [x] Update README/RTK/init validation.
- [x] Add regression and CLI smoke tests.
- [x] Run full verification.
- [x] Produce independent review artifact.
- [x] Close feature only after all checks pass.

## Files allowed to change

- `graph_harness/**`
- `tests/**`
- `docs/**`
- `skills/registry.json`
- `specs/009-control-plane-extensions/**`
- `README.md`
- `RTK.md`
- `feature_list.json`
- `progress/**`
- `init.sh`
- `.graph-harness/**` only for repository-local example/default control files when required

## Files not to change

- Existing executable graph schemas unless compatibility evidence requires it.
- Existing feature 008 specification except for links from new documentation.
- Existing translated READMEs in this feature.

## Verification commands

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q graph_harness
./init.sh
python3 -m graph_harness preflight --root .
python3 -m graph_harness bootstrap --root /tmp/graph-harness-bootstrap-smoke --dry-run
python3 -m graph_harness skills --registry skills/registry.json
```
