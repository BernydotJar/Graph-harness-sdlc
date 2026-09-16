# Current Progress

## Active Feature

None.

## Completed Feature

`009-control-plane-extensions` — `done` — SHIP mode.

## Outcome

Graph Harness SDLC now has a provider-neutral organization/context control plane around the existing executable graph kernel without changing `graph_harness/model.py`, `graph_harness/store.py`, or `graph_harness/runtime.py`.

Delivered:

- GH-F1 hierarchical policy with monotonic safety constraints;
- GH-F2 pre-action allow/warn/deny evaluation;
- GH-F3 coding-agent provider projection contract for Claude/Codex/Gemini;
- GH-F4 generic identity/environment/framework preflight and non-destructive bootstrap;
- GH-F5 read-only doctor and projection drift detection;
- GH-F6 lowest-precedence developer preference profiles;
- GH-F7 stable/experimental skill lifecycle registry;
- GH-F8 provider-neutral local execution attribution with transport disabled by default.

UiPath/RPA is intentionally not a required provider or runtime dependency. Deterministic workflow technology belongs in optional skills or consuming-repository adapters when a product benefits from it.

## Closure Evidence

```text
./init.sh: PASS
unittest: 27/27 PASS
compileall: PASS
preflight CLI smoke: PASS
bootstrap dry-run smoke: PASS
skills registry smoke: PASS
doctor smoke: PASS with only expected optional-bootstrap warnings
execution kernel changed files: none
reverse dependency check from kernel to control-plane modules: none
```

Review artifact:

- `progress/review_009-control-plane-extensions.md`

## Non-blocking Note

The Cloud Sandbox generic `project_verify` helper attempted `.venv/bin/python -m pytest`, but this repository's canonical dependency-free verification path is `./init.sh` / `unittest`; no `.venv` or pytest dependency is required by the project.

## Authority Boundary

This closes the framework implementation increment. It does not grant release, deployment, merge to protected branches, secret mutation, external telemetry transport, package installation, or deterministic workflow execution authority beyond separately approved actions.
