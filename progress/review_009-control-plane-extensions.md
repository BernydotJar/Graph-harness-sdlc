# Review — 009-control-plane-extensions

## Scope

SHIP-mode review of the Foundation-inspired control-plane extensions. The approved architectural constraint is that the Graph Harness execution kernel remains vendor-neutral and useful for AI-only projects; deterministic workflow products such as UiPath are optional skills/integrations, not required framework layers.

## Architecture review

PASS.

- `graph_harness/model.py`, `graph_harness/store.py`, and `graph_harness/runtime.py` are unchanged by this feature.
- No execution-kernel file imports `policy`, `providers`, `bootstrap`, `doctor`, `profiles`, `skills`, or `telemetry`.
- Provider-specific behavior is isolated under `graph_harness/providers/`.
- Built-in provider projections are limited to coding-agent instruction surfaces: Claude, Codex, and Gemini.
- UiPath is explicitly not a built-in provider and requires no runtime dependency. Technology-specific deterministic workflow knowledge can be added independently through skills or consuming-repository adapters.
- Existing runtime CLI syntax remains covered by regression tests.

## Security / policy review

PASS after fixer cycle.

Verified behaviors:

- Safety constraints compose monotonically across broad-to-specific policy layers.
- Policy layers supplied out of hierarchy order fail closed.
- Developer profiles are weaker than policy preferences and cannot define safety/approval/permission bypasses.
- Secret-like keys are rejected from developer profiles, preflight expectations, and attribution contracts.
- Secret-like credential values are also rejected even when stored under benign-looking keys.
- Secret-like write content is an absolute deny even when an action is marked approved.
- Explicitly denied command/path rules cannot be approved away.
- Package installation and destructive actions require explicit approval.
- Pre-action evaluation does not execute the proposed action.

## Bootstrap / identity review

PASS.

- Preflight is read-only.
- It reports work root, Git root, branch, origin, HEAD, dirty state, project state, Python, required commands, and generic framework markers.
- Generic stack detection includes Python, Node/Next.js/React, Terraform, Docker, Android/Gradle, Rust, and .NET markers without vendor-specific RPA logic.
- Expectation identity mismatch fails closed.
- Bootstrap dry-run creates no files.
- Bootstrap apply only creates missing files and preserves existing files.

## Provider projection / drift review

PASS after fixer cycle.

- Target root is explicit; no user home is implicitly selected.
- Apply requires an existing target root.
- Existing generated targets are backed up before replacement.
- Existing invalid provider manifests are detected before target mutation.
- Applied projections record hashes in a local manifest.
- Doctor detects target/source drift and does not repair automatically.

## Skill lifecycle / attribution review

PASS.

- `skills/registry.json` is the canonical stable/experimental registry.
- Registry validation rejects duplicate IDs, unsupported states, path traversal, and missing skill files.
- Existing seven generic skills are registered as stable.
- Attribution is provider-neutral local metadata only; outbound transport remains disabled by default.
- Executor provider/model fields are metadata, not kernel dependencies.

## Fixer findings resolved during review

1. **Developer profile precedence** — initial implementation allowed profile preferences to override project preferences. Fixed so profile preferences are the weakest preference layer and policy wins.
2. **Policy layer order** — initial resolver trusted caller ordering. Fixed to reject project-to-workspace or other decreasing scope order.
3. **Secret-like values** — initial validation rejected secret-like keys but not credential-looking values under benign keys. Fixed with recursive value checks.
4. **Provider manifest failure ordering** — initial apply could mutate the generated target before discovering an invalid existing manifest. Fixed by validating the manifest before target mutation.
5. **Generic CA-A0 stack detection** — extended preflight with provider-neutral framework detection rather than embedding UiPath-specific project states in core.

## Verification evidence

```text
python3 -m unittest discover -s tests -v
27 tests PASS

python3 -m compileall -q graph_harness
PASS

python3 -m graph_harness preflight --root . --require-command git
PASS

python3 -m graph_harness bootstrap --root . --dry-run
PASS; no .graph-harness control files written

python3 -m graph_harness skills --registry skills/registry.json
PASS; 7 stable skills

python3 -m graph_harness doctor --root .
PASS with expected warnings because this repository has not applied its own optional bootstrap files
```

## Remaining non-blocking limitations

- Tool interception is a provider-neutral evaluator/API; automatic wiring into every external coding-agent hook system is intentionally left to provider/integration adapters.
- Provider projection manifests are local JSON files, not a remote configuration service.
- Attribution is local only; no OpenTelemetry transport is included.
- Specialized deterministic workflow skills, including any future UiPath skill, remain separate follow-up work rather than core dependencies.

## Review result

**PASS — ready for final harness validation and closure.**
