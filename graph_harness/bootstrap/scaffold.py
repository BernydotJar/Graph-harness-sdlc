from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..model import ValidationError


@dataclass(frozen=True)
class BootstrapAction:
    path: str
    action: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "action": self.action}


@dataclass(frozen=True)
class BootstrapPlan:
    root: str
    actions: tuple[BootstrapAction, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "graph-harness.bootstrap-plan.v1",
            "root": self.root,
            "actions": [action.as_dict() for action in self.actions],
        }


def starter_files(project_name: str) -> dict[str, str]:
    policy = {
        "schema_version": "graph-harness.policy.v1",
        "scope": "project",
        "safety": {
            "deny_command_patterns": [],
            "warn_command_patterns": [],
            "deny_path_patterns": [],
            "approval_required_patterns": [],
            "secret_patterns": [],
        },
        "preferences": {},
    }
    profile = {
        "schema_version": "graph-harness.developer-profile.v1",
        "developer": None,
        "preferences": {},
    }
    attribution = {
        "schema_version": "graph-harness.attribution.v1",
        "project": project_name,
        "engagement": None,
        "workflow": {"kind": "software-delivery"},
        "executor": {"provider": None, "model": None},
        "metadata": {},
    }
    providers_readme = """# Provider deltas\n\nOptional provider-specific instruction deltas live here. Shared policy remains provider-neutral.\n\nBuilt-in coding-agent projections currently support Claude, Codex, and Gemini. Specialized product or deterministic-workflow integrations belong in skills/adapters and are not required by the Graph Harness kernel.\n"""
    return {
        ".graph-harness/policy.json": json.dumps(policy, indent=2, sort_keys=True) + "\n",
        ".graph-harness/developer.json": json.dumps(profile, indent=2, sort_keys=True) + "\n",
        ".graph-harness/attribution.json": json.dumps(attribution, indent=2, sort_keys=True) + "\n",
        ".graph-harness/providers/README.md": providers_readme,
    }


def plan_bootstrap(root: str | Path) -> BootstrapPlan:
    candidate = Path(root).expanduser().resolve(strict=False)
    project_name = candidate.name or "project"
    actions = []
    for relative_path in starter_files(project_name):
        target = candidate / relative_path
        actions.append(BootstrapAction(relative_path, "skip-existing" if target.exists() else "create"))
    return BootstrapPlan(str(candidate), tuple(actions))


def apply_bootstrap(root: str | Path, *, dry_run: bool = True) -> BootstrapPlan:
    candidate = Path(root).expanduser().resolve(strict=False)
    if not candidate.is_dir():
        raise ValidationError(f"bootstrap root must already exist: {candidate}")
    plan = plan_bootstrap(candidate)
    if dry_run:
        return plan
    content_by_path = starter_files(candidate.name or "project")
    for action in plan.actions:
        if action.action != "create":
            continue
        target = candidate / action.path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(content_by_path[action.path])
        except FileExistsError:
            continue
    return plan
