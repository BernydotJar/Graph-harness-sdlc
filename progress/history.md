# History

## 001-harness-bootstrap

- Created initial harness structure.
- Created command contracts.
- Created Claude agent role files.
- Created docs and templates.
- Added README workflow diagrams and ASCII harness cat mascot.
- Added P0/P1 harness hardening docs, skills, ADRs, review templates, prompts, and examples.
- Created first SDD spec.
- Set status to `spec_ready`.
- Stopped for human approval.

## 008-executable-graph-runtime

- User directive approved bounded framework runtime and application-adapter work; normalized directive SHA-256 `992ba3453c36d0d09aea7af7ea89d5f84da5b63d998342c7631e4a94a797e142`.
- Added a dependency-free Python runtime with typed project, event, node, gate, and derived-state contracts.
- Added append-only JSONL persistence with sequence, POSIX locking, optimistic concurrency, fsync, and SHA-256 hash chaining.
- Added dependency readiness, explicit approval, lifecycle transition enforcement, evidence freshness, gate evaluation, checkpoints, and localized repair.
- Added versioned JSON schemas and six fail-closed unit tests.
- Built and installed wheel `graph_harness_sdlc-0.1.0-py3-none-any.whl`; SHA-256 `a8ddf7fadeed0a68d30a5f30f08ddc561a5d2e3edbf88c1b6a9f4db61617f9fd`.
- Set feature to `review`; application adoption, exact-head CI, human close, and merge remain pending.

## 2026-07-29 — 008 closure

- Cross-repository application adoption passed exact-head run `30428010235` at `655df8b0317482001a5dbe7a4483411318f14dfd`.
- The application exercised localized repair: only `INC-038` was invalidated and advanced to revision 1 before all eight jobs passed.
- User authorized closure and merge; approval SHA-256 `177e06b3b8e83da64c16b2991d25f1e6f36a3b576c7e47f176549317fc5843cc`.
- Feature `008-executable-graph-runtime` transitioned from `review` to `done`.

## 009-control-plane-extensions

- User explicitly approved the Foundation-inspired control-plane work with the architectural constraint that UiPath/RPA remain optional rather than becoming a framework center.
- Added provider-neutral hierarchical policy resolution with monotonic safety constraints and broad-to-specific scope validation.
- Added pre-action allow/warn/deny evaluation for secret-like writes, denied commands/paths, package installs, destructive commands, and approval-gated operations.
- Added explicit-target coding-agent projections for Claude, Codex, and Gemini with dry-run default, backups, provider manifests, and drift checks.
- Added generic CA-A0-style preflight for work root, Git identity, branch/origin/HEAD/dirty state, Python, required commands, project state, and framework markers without UiPath-specific logic.
- Added non-destructive bootstrap, read-only doctor, lowest-precedence developer profiles, stable/experimental skill registry, and local provider-neutral attribution metadata.
- Kept `graph_harness/model.py`, `graph_harness/store.py`, and `graph_harness/runtime.py` unchanged; verified no reverse dependency from the execution kernel into the new control-plane modules.
- Review found and fixed profile-precedence semantics, policy layer ordering, secret-looking values under benign keys, provider-manifest validation ordering, and generic stack detection.
- Canonical closure verification: `./init.sh` PASS, 27/27 unit tests PASS, compileall PASS, preflight/bootstrap/skills/doctor CLI smokes PASS.
- Feature transitioned from `review` to `done` after `progress/review_009-control-plane-extensions.md` passed.
