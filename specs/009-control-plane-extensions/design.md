# 009 — Design

## Architectural decision

The executable graph kernel remains isolated:

```text
graph_harness/model.py
  + graph_harness/store.py
  + graph_harness/runtime.py
        = execution control plane
```

Foundation-inspired capabilities surround that kernel rather than replacing it:

```text
Context / organization plane
  policy hierarchy
  developer profile
  provider projections
  bootstrap / preflight
  skills registry
  attribution metadata
        |
        v
Graph execution plane
  typed nodes
  state transitions
  approvals
  revisions
  localized repair
        |
        v
Evidence / audit plane
  append-only event ledger
  evidence freshness
  gate evaluation
        |
        v
Product / platform plane
  application code
  AI systems
  APIs
  web/mobile/data/infra
  optional deterministic workflows
```

No vendor-specific automation platform is a required layer. A deterministic workflow engine may be used when its semantics are preferable for a task, but it is an optional integration surface.

## Module boundaries

```text
graph_harness/
  model.py                 existing execution kernel
  store.py                 existing execution kernel
  runtime.py               existing execution kernel
  cli.py                   command routing only

  policy/
    __init__.py
    model.py               policy contracts
    resolver.py            hierarchical composition
    enforcement.py         pre-action allow/warn/deny

  providers/
    __init__.py
    base.py                provider adapter contract
    builtins.py            Claude/Codex/Gemini projections

  bootstrap/
    __init__.py
    preflight.py           identity/environment inspection
    scaffold.py            non-destructive bootstrap plan/apply

  doctor.py                read-only drift detection
  profiles.py              developer preference profile
  skills.py                skill registry lifecycle
  telemetry.py             provider-neutral attribution
```

The new modules may import shared standard-library utilities, but the execution kernel must not import them. This preserves the dependency direction.

## GH-F1 policy model

A policy document is JSON:

```json
{
  "schema_version": "graph-harness.policy.v1",
  "scope": "project",
  "safety": {
    "deny_command_patterns": [],
    "warn_command_patterns": [],
    "deny_path_patterns": [],
    "approval_required_patterns": [],
    "secret_patterns": []
  },
  "preferences": {
    "response_style": "concise"
  }
}
```

Resolution order is broad to specific. Safety collections are unioned and deduplicated. Preferences are shallow-merged with later layers winning. This intentionally makes safety monotonic while allowing local ergonomic preferences.

## GH-F2 action enforcement

An action request has:

```text
kind        shell | write | network | generic
command     optional shell/tool text
paths       zero or more target paths
content     optional write payload
approved    explicit caller-provided approval bit
```

The evaluator applies built-in high-confidence safety checks plus resolved policy:

1. secret-like content -> deny;
2. absolute denied command/path -> deny;
3. install/destructive/approval-required pattern without approval -> deny;
4. warning pattern -> warn;
5. otherwise -> allow.

The evaluator never executes a command.

## GH-F3 provider adapters

A provider adapter describes a generated instruction projection:

```text
provider_id
relative_target
render(shared_text, provider_delta, profile_preferences)
plan(...)
apply(...)
```

Built-ins:

- Claude -> `.claude/CLAUDE.md`
- Codex -> `.codex/AGENTS.md`
- Gemini -> `.gemini/GEMINI.md`

The caller supplies the target root. No home directory is implicitly assumed by the core API. Apply backs up an existing target before replacement. Dry-run returns the plan only.

UiPath is deliberately not a built-in provider adapter because it is not a universal coding-agent provider requirement. UiPath-specific workflows can be packaged as a skill or integration adapter without altering this contract.

## GH-F4 preflight and bootstrap

Preflight inspects:

- resolved work root;
- Git root;
- branch;
- origin;
- HEAD;
- dirty state;
- Python version;
- requested command versions/availability.

An expectation file uses `graph-harness.preflight.v1` and may constrain repository/origin/work-root and required commands. Keys that look like secrets are rejected before use.

Bootstrap creates a small `.graph-harness/` control directory containing starter policy, developer profile, attribution config, and provider delta directory. The planner marks each path as `create` or `skip-existing`. Apply creates only planned new files.

## GH-F5 doctor

Doctor is read-only. It combines:

- preflight result;
- policy/profile/attribution parsing;
- skill registry validation;
- provider manifest checks.

Provider projection apply writes `.graph-harness/provider-manifest.json` containing only paths and hashes. Doctor compares recorded source/render hashes with current files and reports drift. It does not repair.

## GH-F6 developer profiles

Developer profiles use `graph-harness.developer-profile.v1`:

```json
{
  "schema_version": "graph-harness.developer-profile.v1",
  "developer": "optional-display-id",
  "preferences": {}
}
```

Only `preferences` is behavioral input. Safety-like keys are rejected recursively. Profiles are merged after policy preferences, but cannot modify safety constraints.

## GH-F7 skill registry

`skills/registry.json` is the canonical catalog:

```json
{
  "schema_version": "graph-harness.skills.v1",
  "skills": [
    {
      "id": "spec-authoring",
      "path": "skills/spec-authoring/skill.md",
      "status": "stable",
      "description": "..."
    }
  ]
}
```

Allowed lifecycle states: `stable`, `experimental`.

Specialized technology skills may be registered without introducing runtime imports. This is the intended home for optional RPA or deterministic-workflow knowledge.

## GH-F8 attribution

Attribution config uses `graph-harness.attribution.v1` and remains local data until an external adapter explicitly exports it. Canonical keys include:

- `project`
- `engagement`
- `workflow.kind`
- `executor.provider`
- `executor.model`

Values are normalized to a safe compact representation. Secret-like keys are rejected.

## CLI

Existing runtime commands remain backwards compatible. `--project` and `--events` become conditionally required only for runtime commands.

New commands:

```text
policy-resolve
check-action
preflight
bootstrap
provider-render
doctor
skills
attribution
```

All mutating commands expose `--dry-run` or require an explicit apply flag.

## Failure behavior

- malformed control-plane contracts -> exit 2 with a precise validation error;
- identity mismatch -> preflight `ok=false`, CLI exit 2;
- denied action -> structured deny result, CLI exit 3;
- doctor error finding -> exit 2;
- doctor warning without errors -> exit 0;
- dry-run never writes.
