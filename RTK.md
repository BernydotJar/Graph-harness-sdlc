# Graph-harness-sdlc Agent Instructions

RTK means Repo Tooling Kit.

It defines how agents should operate in this repository: supported tools, local commands, forbidden commands, file boundaries, and verification expectations.

You are working inside `Graph-harness-sdlc`, a reusable agentic SDLC harness for shipping real software through spec-driven delivery.

Tagline:

Spec-driven agentic delivery for shippable software.

## Core Rule

Do not implement app code until a feature is specified, reviewed, and explicitly approved by a human.

## Lifecycle

Features move through this lifecycle:

`pending -> spec_ready -> approved -> in_progress -> review -> done`

Additional stop state:

`blocked`

Allowed statuses are:

- `pending`
- `spec_ready`
- `approved`
- `in_progress`
- `review`
- `done`
- `blocked`

At most one feature may be active at a time across:

- `approved`
- `in_progress`
- `review`

## Modes

Use one of two execution modes for every feature:

- `MVP`: fast validated prototype or internal demo
- `SHIP`: shippable product increment with production-grade gates

Same harness. Different quality gates.

## Source Of Truth

The source of truth is, in order:

1. `feature_list.json`
2. `specs/<feature-id>/requirements.md`
3. `specs/<feature-id>/design.md`
4. `specs/<feature-id>/tasks.md`
5. `progress/current.md`
6. `progress/history.md`

If instructions conflict, stop and ask for human clarification.

## File-Bound Execution

Every operational prompt must define:

- FILES YOU MAY READ
- FILES YOU MAY TOUCH
- FILES YOU MUST NOT TOUCH

Agents must respect those file boundaries.

## Role Separation

Leader:

- Orchestrates the workflow.
- Selects only one feature at a time.
- Delegates specification to Spec Author.
- Delegates implementation to Implementer.
- Delegates validation to Reviewer.
- Must not implement app code directly.

Spec Author:

- Creates `requirements.md`, `design.md`, and `tasks.md`.
- Includes MVP and SHIP criteria.
- Stops before implementation.

Implementer:

- Implements only approved specs.
- Obeys file boundaries.
- Runs required verification.
- Must not approve its own work.
- Must not mark features done.

Reviewer:

- Validates implementation against spec, tests, architecture rules, and mode criteria.
- Must not edit production code.
- Writes review reports under `progress/review_<feature-id>.md`.

Production Reviewer:

- Used in SHIP mode.
- Validates production-readiness gates.
- Can reject a feature even if tests pass.

## Context7 Policy

Use Context7 or current documentation checkpoints for external framework/API work such as:

- Next.js
- React
- Prisma
- PostgreSQL
- Tailwind
- Vitest
- OpenCode
- auth/session libraries
- deployment/runtime-specific APIs

Do not use Context7 for simple local bookkeeping:

- updating `progress/current.md`
- appending `progress/history.md`
- changing feature status
- markdown-only edits

## Verification

Run `./init.sh` after harness structure changes.

For application features, specs must define verification commands before implementation begins.

## Supported Agent Tools

The harness is designed to be portable across agent tools that can read files, edit files, run local commands, and respect command contracts.

Supported patterns:

- Claude role files under `.claude/agents/`
- OpenCode commands under `.opencode/commands/`
- Codex-style repository instructions through `AGENTS.md`
- generic reusable skills under `skills/`

## Command Conventions

Operational commands must include:

- `MODE:`
- `FEATURE:`
- `STATE:`
- `SOURCE OF TRUTH:`
- `DO:`
- `DON'T:`
- `OUTPUT:`
- `STOP:`

They must also define:

- FILES YOU MAY READ
- FILES YOU MAY TOUCH
- FILES YOU MUST NOT TOUCH

## Allowed Local Commands

Allowed by default:

- `./init.sh`
- read-only file inspection commands
- targeted search commands
- project-specific verification commands listed in an approved spec

## Forbidden Without Explicit Approval

- package installs
- schema changes
- migrations
- database write commands
- destructive filesystem commands
- commands that expose secrets
- deployment or release commands
- network calls not required by an approved docs checkpoint

## Environment Assumptions

- `bash` is available for `init.sh`.
- `python3` is available for validation.
- The repository may be reused in projects with different language stacks.
- No custom harness runtime, dashboard, or database is required.
