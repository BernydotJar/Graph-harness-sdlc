#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(".")

required_files = [
    "AGENTS.md",
    "RTK.md",
    "CLAUDE.md",
    "README.md",
    "feature_list.json",
    "init.sh",
    "docs/methodology.md",
    "docs/modes.md",
    "docs/production-readiness.md",
    "docs/mcp-context7-policy.md",
    "docs/specs.md",
    "docs/verification.md",
    "docs/conventions.md",
    "templates/feature/requirements.md",
    "templates/feature/design.md",
    "templates/feature/tasks.md",
    "templates/prompts/goal.md",
    "templates/prompts/mvp-mode.md",
    "templates/prompts/ship-mode.md",
    "templates/prompts/production-spec-patch.md",
    "progress/current.md",
    "progress/history.md",
]

command_files = [
    ".opencode/commands/spec-next.md",
    ".opencode/commands/approve-feature.md",
    ".opencode/commands/production-spec-patch.md",
    ".opencode/commands/implement-feature.md",
    ".opencode/commands/review-feature.md",
    ".opencode/commands/close-feature.md",
    ".opencode/commands/status.md",
    ".opencode/commands/verify.md",
    ".opencode/commands/use-context7.md",
]

agent_files = [
    ".claude/agents/leader.md",
    ".claude/agents/spec-author.md",
    ".claude/agents/implementer.md",
    ".claude/agents/reviewer.md",
    ".claude/agents/production-reviewer.md",
]

required_headings = [
    "MODE:",
    "FEATURE:",
    "STATE:",
    "SOURCE OF TRUTH:",
    "DO:",
    "DON'T:",
    "OUTPUT:",
    "STOP:",
]

errors = []

for file_name in required_files + command_files + agent_files:
    if not (root / file_name).is_file():
        errors.append(f"missing required file: {file_name}")

try:
    data = json.loads((root / "feature_list.json").read_text())
except Exception as exc:
    errors.append(f"feature_list.json is not valid JSON: {exc}")
    data = {}

allowed = set(data.get("allowed_statuses", []))
expected = {"pending", "spec_ready", "approved", "in_progress", "review", "done", "blocked"}
if allowed != expected:
    errors.append(f"allowed_statuses must be exactly {sorted(expected)}")

features = data.get("features", [])
if not isinstance(features, list) or not features:
    errors.append("feature_list.json must contain a non-empty features array")

active_statuses = {"approved", "in_progress", "review"}
active = [f.get("id") for f in features if f.get("status") in active_statuses]
if len(active) > 1:
    errors.append(f"at most one active feature is allowed, found: {active}")

spec_required_statuses = {"spec_ready", "approved", "in_progress", "review", "done"}
for feature in features:
    feature_id = feature.get("id")
    status = feature.get("status")
    if status not in expected:
        errors.append(f"{feature_id}: invalid status {status!r}")
    if status in spec_required_statuses:
        for spec_file in ["requirements.md", "design.md", "tasks.md"]:
            path = root / "specs" / str(feature_id) / spec_file
            if not path.is_file():
                errors.append(f"{feature_id}: missing spec file {path}")

for command_file in command_files:
    path = root / command_file
    if not path.is_file():
        continue
    text = path.read_text()
    for heading in required_headings:
        if heading not in text:
            errors.append(f"{command_file}: missing heading {heading}")
    for boundary in ["FILES YOU MAY READ", "FILES YOU MAY TOUCH", "FILES YOU MUST NOT TOUCH"]:
        if boundary not in text:
            errors.append(f"{command_file}: missing boundary {boundary}")

context_policy = root / "docs/mcp-context7-policy.md"
if context_policy.is_file():
    text = context_policy.read_text().lower()
    for term in ["context7", "next.js", "react", "prisma", "postgresql", "tailwind", "vitest"]:
        if term not in text:
            errors.append(f"docs/mcp-context7-policy.md: missing policy term {term}")

if errors:
    print("Harness validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Harness validation passed.")
print(f"Features: {len(features)}")
print(f"Active features: {len(active)}")
PY
