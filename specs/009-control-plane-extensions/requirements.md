# 009 — Foundation-inspired control-plane extensions

## Outcome

Extend Graph Harness SDLC with organization/context-plane capabilities inspired by Agentic Foundation while preserving the executable graph kernel as the source of execution truth.

The resulting framework must remain useful for AI-only software projects. Deterministic workflow platforms, including RPA products, are optional integrations represented through skills or adapters and must never become runtime dependencies of the harness.

## Requirements

### GH-F1 — Policy hierarchy

- Support ordered policy layers from broad to specific scopes such as workspace, customer, solution, project, and repository.
- Safety constraints must compose monotonically: a narrower layer may add restrictions but may not remove an inherited restriction.
- Preferences may be overridden by more-specific layers.
- Policy data must use a provider-neutral, versioned JSON contract.
- Policy resolution must be deterministic and independently testable.

### GH-F2 — Tool interception

- Provide a provider-neutral pre-action evaluator returning `allow`, `warn`, or `deny`.
- Detect high-confidence install commands, destructive shell commands, denied command patterns, denied paths, and secret-like writes.
- Explicit approval may satisfy rules designated as approval-gated, but it must not bypass absolute safety denies.
- The interceptor must not execute the requested action itself.

### GH-F3 — Provider adapter contract

- Define a small adapter contract for coding-agent providers without importing provider SDKs into the execution kernel.
- Ship adapters for Claude, Codex, and Gemini as projections of shared instructions.
- Provider adapters must support dry-run planning and non-destructive writes with backup of an existing generated target.
- UiPath, RPA, and deterministic-workflow products must not be required providers. They belong in optional skills/integrations when used.

### GH-F4 — Bootstrap and preflight

- Add a generic project preflight that reports exact work root, Git root, branch, origin, HEAD, dirty state, Python version, and required command availability.
- Support an optional expectation file for identity and environment requirements.
- Reject secret-like expectation keys and fail closed on identity mismatch.
- Add a non-destructive bootstrap planner and applier.
- `--dry-run` must perform no writes.
- Existing files must not be overwritten by default.

### GH-F5 — Doctor / drift detection

- Add a read-only doctor that checks the project bootstrap surface, policy/profile validity, provider projection manifest, and target/source hash drift.
- Doctor output must distinguish `ok`, `warn`, and `error` findings.
- Drift checks must not silently repair files.

### GH-F6 — Developer profiles

- Support optional developer profiles containing preferences only.
- Developer profiles are lowest-precedence customization and may not contain safety rules, approval bypasses, secrets, or machine credentials.
- Profiles must never weaken inherited project policy.

### GH-F7 — Skill lifecycle

- Add a versioned skill registry with `stable` and `experimental` lifecycle states.
- Registry validation must detect missing skill files, duplicate IDs, unsupported states, and malformed entries.
- Existing framework skills remain provider-neutral.
- Specialized skills such as a UiPath coded-agent workflow may be added independently without changing the Graph Harness kernel.

### GH-F8 — Telemetry attribution

- Add provider-neutral execution attribution metadata without enabling outbound telemetry by default.
- Attribution values must be sanitized and must reject secret-like keys.
- The contract must distinguish executor provider/model metadata from workflow kind, project, and engagement metadata.
- The core runtime must remain functional when no attribution configuration exists.

## Compatibility

- Existing `graph-harness --project ... --events ... <runtime-command>` invocations must continue to work.
- The `graph_harness.model`, `graph_harness.store`, and `graph_harness.runtime` execution semantics must not be weakened.
- No third-party Python dependency may be introduced for these capabilities.

## Security and boundaries

- New control-plane modules are advisory/enforcement helpers around execution; they do not grant deployment, merge, release, credential, migration, or spending authority.
- No provider home directory may be mutated unless the caller explicitly invokes an apply operation.
- Dry-run paths must be mechanically side-effect free.
- Secrets must not be printed into generated manifests, profile files, policy files, or telemetry attribution.

## Verification

- Existing runtime unit tests remain green.
- Add regression tests for every GH-F1 through GH-F8 capability.
- `./init.sh` passes.
- `python3 -m unittest discover -s tests -v` passes.
- `python3 -m compileall -q graph_harness` passes.
- CLI smoke tests cover preflight, policy resolution, action checking, provider dry-run, bootstrap dry-run, doctor, skills registry, and attribution rendering.

## Non-goals

- Replacing the Graph Harness execution runtime with Agentic Foundation.
- Reproducing Agentic Foundation's PowerShell implementation.
- Making UiPath or any RPA platform a mandatory architectural layer.
- Adding model-specific benchmark logic.
- Installing external tooling or provider SDKs.
- Automatically sending telemetry to an external collector.
