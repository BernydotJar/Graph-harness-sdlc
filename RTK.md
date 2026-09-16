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

`pending -> spec_ready -> approved -> ready -> running -> review -> done`

Failure recovery uses `repair_required`; terminal replacement uses `superseded`.

Additional stop state:

`blocked`

Allowed statuses are:

- `pending`
- `spec_ready`
- `approved`
- `ready`
- `running`
- `review`
- `done`
- `blocked`
- `repair_required`
- `superseded`

At most one feature may be active at a time across:

- `approved`
- `ready`
- `running`
- `review`
- `repair_required`

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

## Executable Runtime

The reusable runtime is the `graph_harness` Python package. Consuming repositories provide a versioned `graph-harness.project.v1` document and an append-only `graph-harness.event.v1` JSONL store.

The runtime owns typed transitions, dependency readiness, evidence freshness, gate evaluation, checkpoints, and localized repair. Application repositories own their requirements, task ledgers, domain evidence, and adapters into the framework contract. They must pin the framework revision rather than copy runtime modules.

Source execution requires Python 3.11+ and no third-party dependency:

```bash
python3 -m graph_harness --project <project.json> --events <events.jsonl> validate
```

## Control-Plane Boundaries

`graph_harness.model`, `graph_harness.store`, and `graph_harness.runtime` are the execution kernel. They must remain provider- and vendor-neutral.

The following are peripheral control-plane modules and must not become reverse dependencies of the kernel:

- `graph_harness.policy` — hierarchical policy and pre-action enforcement;
- `graph_harness.providers` — coding-agent instruction projections;
- `graph_harness.bootstrap` — identity/environment preflight and non-destructive bootstrap;
- `graph_harness.doctor` — read-only drift detection;
- `graph_harness.profiles` — developer preferences only;
- `graph_harness.skills` — stable/experimental capability registry;
- `graph_harness.telemetry` — local attribution metadata with no transport by default.

Policy safety is monotonic: narrower scopes may add restrictions and may never remove inherited restrictions. Developer profiles are weaker than policy and may not contain safety, permission, approval-bypass, credential, token, password, or secret fields.

`bootstrap` and `provider-render` are dry-run by default and require `--apply` for writes. `doctor`, `preflight`, `policy-resolve`, `check-action`, `skills`, and `attribution` do not perform the evaluated external action.

UiPath, RPA platforms, workflow engines, cloud services, databases, frameworks, and other product technologies are optional skills or consuming-repository integrations. None is a mandatory architectural layer of Graph Harness SDLC. Use deterministic workflows where stable rules and transactional behavior make them the better executor; use AI where semantic reasoning and adaptation are required.

See `docs/control-plane.md` and `docs/deterministic-workflows.md`.

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

Control-plane changes must additionally verify:

- existing runtime tests remain green;
- dry-run commands make no writes;
- policy inheritance cannot weaken safety;
- provider projections are explicit-target only;
- doctor reports drift without repairing it;
- skill registry and attribution contracts validate without external dependencies.

## Supported Agent Tools

The harness is designed to be portable across agent tools that can read files, edit files, run local commands, and respect command contracts.

Supported patterns:

- Claude role files under `.claude/agents/`
- OpenCode commands under `.opencode/commands/`
- Codex-style repository instructions through `AGENTS.md`
- generic reusable skills under `skills/`
- optional generated instruction projections for Claude, Codex, and Gemini through `graph_harness.providers`

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
- read-only Graph Harness control-plane commands such as `preflight`, `doctor`, `policy-resolve`, `skills`, and `attribution`

## Forbidden Without Explicit Approval

- package installs
- schema changes
- migrations
- database write commands
- destructive filesystem commands
- commands that expose secrets
- deployment or release commands
- network calls not required by an approved docs checkpoint
- `bootstrap --apply` or `provider-render --apply` against a target outside the approved work boundary

## Environment Assumptions

- `bash` is available for `init.sh`.
- `python3` is available for validation.
- The repository may be reused in projects with different language stacks.
- No custom harness dashboard or database is required.
- The execution kernel and control plane require no third-party Python dependency.
