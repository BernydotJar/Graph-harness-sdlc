# 001-harness-bootstrap Design

## Approach

Create a minimal but complete harness skeleton with structured instructions, command contracts, role definitions, documentation, templates, progress files, and a validation script.

The bootstrap stops at `spec_ready`. It prepares the repo for human approval and future implementation cycles.

## Files You May Read

- `feature_list.json`
- `README.md`
- `AGENTS.md`
- `RTK.md`
- `CLAUDE.md`
- `.opencode/commands/**`
- `.claude/agents/**`
- `docs/**`
- `templates/**`
- `progress/**`
- `specs/001-harness-bootstrap/**`

## Files You May Touch

- `AGENTS.md`
- `RTK.md`
- `CLAUDE.md`
- `README.md`
- `feature_list.json`
- `init.sh`
- `.opencode/commands/**`
- `.claude/agents/**`
- `docs/**`
- `templates/**`
- `progress/current.md`
- `progress/history.md`
- `specs/001-harness-bootstrap/**`

## Files You Must Not Touch

- application source files
- package manifests
- lockfiles
- environment files
- secrets
- deployment configuration

## Data Contracts

`feature_list.json` is the feature registry.

Required top-level fields:

- `repository`
- `tagline`
- `allowed_statuses`
- `features`

Required feature fields:

- `id`
- `title`
- `mode`
- `status`
- `summary`

Allowed statuses:

- `pending`
- `spec_ready`
- `approved`
- `in_progress`
- `review`
- `done`
- `blocked`

## Dependencies

No external dependencies are required.

`init.sh` uses the system `python3` interpreter.

## Context7 Checkpoints

No Context7 checkpoint is required for this bootstrap because it is markdown and local validation only.

The policy is documented for future framework/API work.

## Risks

- Risk: command files become inconsistent.
  - Mitigation: `init.sh` validates required command headings and file-bound sections.
- Risk: multiple features become active.
  - Mitigation: `init.sh` validates active feature count.
- Risk: specs are skipped.
  - Mitigation: `init.sh` validates spec files for post-pending states.

## Verification Plan

Run:

```sh
./init.sh
```

Expected result:

```text
Harness validation passed.
```

