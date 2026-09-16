# Control Plane Extensions

Graph Harness SDLC separates execution correctness from organizational context and developer ergonomics.

The executable graph kernel remains authoritative for work state, evidence freshness, approvals, gates, revisions, and localized repair. Context-plane capabilities surround that kernel and may be adopted independently.

## Architecture

```text
Context / organization plane
  policy hierarchy
  developer profiles
  provider projections
  bootstrap / preflight
  skills lifecycle
  attribution metadata
        |
        v
Graph execution plane
  typed nodes
  dependencies
  scheduler readiness
  approvals
  state transitions
  revisions
  localized repair
        |
        v
Evidence / audit plane
  event ledger
  hashes
  evidence
  gate evaluations
  checkpoints
        |
        v
Product / platform plane
  AI applications
  APIs and services
  web / mobile
  data systems
  infrastructure
  optional deterministic workflows
```

This is deliberately not a single-vendor architecture. A project may use only AI and application code. Another project may combine probabilistic agents with deterministic workflows. Neither path changes the Graph Harness kernel.

## Policy hierarchy

Policies use `graph-harness.policy.v1` and are resolved broad to specific:

```text
organization
  -> workspace
  -> customer
  -> solution
  -> project
  -> repository
```

Safety constraints are monotonic. A narrower scope may add restrictions but cannot remove inherited restrictions.

Preferences are different. They may be refined by more-specific policy. A developer profile is weaker than every policy layer: it may supply a preference only when project policy does not override it.

Example:

```json
{
  "schema_version": "graph-harness.policy.v1",
  "scope": "project",
  "safety": {
    "deny_command_patterns": ["git\\s+push\\s+--force"],
    "warn_command_patterns": [],
    "deny_path_patterns": ["*/production-secrets/*"],
    "approval_required_patterns": ["terraform\\s+apply"],
    "secret_patterns": []
  },
  "preferences": {
    "review_detail": "high"
  }
}
```

Resolve layers with:

```bash
python3 -m graph_harness policy-resolve \
  --layer /path/to/workspace-policy.json \
  --layer /path/to/project-policy.json \
  --profile /path/to/developer.json \
  --pretty
```

## Pre-action enforcement

`check-action` evaluates a proposed operation without executing it.

Results are:

- `allow` — no blocking policy matched;
- `warn` — an advisory pattern matched;
- `deny` — an absolute deny matched, or an approval-gated action lacks explicit approval.

High-confidence built-in checks include package/internet installs, destructive shell commands, secret-like writes, and policy-denied paths or commands.

```bash
python3 -m graph_harness check-action \
  --layer .graph-harness/policy.json \
  --command-line 'pip install example'
```

The evaluator does not create authority. Passing `--approved` can satisfy approval-gated rules such as package installation, but cannot override an absolute deny such as secret-like content or an explicitly denied command.

## Preflight

`preflight` is read-only and reports:

- exact work root;
- Git root;
- branch;
- origin;
- HEAD;
- dirty state;
- Python version;
- required command availability and version output;
- generic framework markers such as Python, Node/Next.js, Terraform, Docker, Android/Gradle, Rust, or .NET.

```bash
python3 -m graph_harness preflight --root . --require-command git --pretty
```

An optional `graph-harness.preflight.v1` expectation file can fail closed on identity mismatch:

```json
{
  "schema_version": "graph-harness.preflight.v1",
  "identity": {
    "repository": "owner/repo",
    "branch": "main"
  },
  "environment": {
    "python": ">=3.11",
    "require_commands": ["git"],
    "frameworks": ["python"]
  }
}
```

Secret-like keys are rejected from expectation files.

## Bootstrap

Bootstrap initializes only the provider-neutral control surface:

```text
.graph-harness/
  policy.json
  developer.json
  attribution.json
  providers/README.md
```

Dry-run is the default:

```bash
python3 -m graph_harness bootstrap --root . --dry-run --pretty
```

Apply must be explicit:

```bash
python3 -m graph_harness bootstrap --root . --apply --pretty
```

Existing files are skipped, never overwritten.

## Coding-agent provider projections

Provider adapters are projections of shared instructions, not sources of truth. Built-ins currently exist for:

- Claude;
- Codex;
- Gemini.

The target root is always explicit. The harness does not assume or mutate a user's home directory by default.

```bash
python3 -m graph_harness provider-render \
  --provider codex \
  --root /explicit/target/root \
  --shared-file AGENTS.md \
  --dry-run \
  --pretty
```

Applying a projection backs up an existing generated target and records a hash manifest for later drift checks.

Provider adapters are for coding-agent instruction projections. Product technologies and deterministic automation platforms do not belong in this built-in provider list; they are optional skills or integration adapters.

## Doctor

`doctor` is read-only. It checks:

- preflight identity/environment state;
- control-plane contract validity;
- skill registry validity;
- provider target drift;
- provider source drift.

```bash
python3 -m graph_harness doctor --root . --pretty
```

Doctor reports drift. It never silently re-renders or repairs a target.

## Developer profiles

Developer profiles use `graph-harness.developer-profile.v1`:

```json
{
  "schema_version": "graph-harness.developer-profile.v1",
  "developer": "optional-id",
  "preferences": {
    "editor": "vim",
    "response_detail": "concise"
  }
}
```

Profiles may not contain safety, approval, permission, bypass, credential, token, password, or secret fields. They cannot weaken policy.

## Skill lifecycle

`skills/registry.json` uses `graph-harness.skills.v1` and defines two lifecycle states:

- `stable` — supported reusable capability;
- `experimental` — available for testing but not yet part of the stable surface.

```bash
python3 -m graph_harness skills --registry skills/registry.json --pretty
```

Specialized technologies can be added as skills without changing the runtime. For example, a future UiPath coded-agent skill can describe UiPath-native lifecycle rules while remaining completely optional for teams that do not use UiPath or RPA.

## Attribution

`graph-harness.attribution.v1` records local execution metadata such as:

- project;
- engagement;
- workflow kind;
- executor provider;
- executor model.

```bash
python3 -m graph_harness attribution --config .graph-harness/attribution.json --pretty
```

The core only renders sanitized local attributes. `transport_enabled` is false: sending data to OpenTelemetry or another collector requires a separate explicit integration.

## Design constraint

These capabilities are not permitted to pull the execution kernel toward a specific provider, model, automation vendor, or project type.

The dependency direction is one-way:

```text
control-plane helpers -> execution kernel APIs
execution kernel -X-> provider/bootstrap/profile/telemetry modules
```

That constraint is what keeps Graph Harness usable for AI-only engineering as well as hybrid systems that combine AI with deterministic software workflows.
