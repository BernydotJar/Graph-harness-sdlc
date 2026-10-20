"""Fail-closed SHIP product acceptance based on complete, independently evidenced actions.

This is a product-level gate, not a replacement for the execution graph. A green E2E
is a single proof; it cannot approve untested actions, missing UI, or stale production.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .model import ValidationError

KINDS = ("implementation", "ui", "journey", "production")
FORBIDDEN_MODES = ("mock", "synthetic", "fixture", "stub", "demo")


def _read_json(path: str | Path) -> Mapping[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"expected object: {path}")
    return data


def _unique_strings(values: Any, label: str) -> list[str]:
    if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValidationError(f"{label} must be a nonempty array of strings")
    if len(set(values)) != len(values):
        raise ValidationError(f"{label} contains duplicates")
    return values


def _artifact_valid(item: Mapping[str, Any], repo_root: Path) -> bool:
    artifact = item.get("artifact")
    digest = item.get("sha256")
    if not isinstance(artifact, str) or not artifact or not isinstance(digest, str) or len(digest) != 64:
        return False
    # No absolute, parent traversal, symlink escape or empty artifact proof.
    if Path(artifact).is_absolute() or ".." in Path(artifact).parts:
        return False
    path = (repo_root / artifact).resolve()
    if not path.is_relative_to(repo_root.resolve()) or not path.is_file():
        return False
    return bool(path.stat().st_size) and hashlib.sha256(path.read_bytes()).hexdigest() == digest.lower()


def assess_product_acceptance(
    manifest: Mapping[str, Any],
    evidence: Mapping[str, Any],
    *,
    repo_root: str | Path,
    source_revision: str,
    production_revision: str | None = None,
) -> dict[str, Any]:
    """Evaluate *all* critical actions; anything missing, stale or self-reviewed blocks GO."""
    if manifest.get("schema_version") != "graph-harness.product-acceptance.v1":
        raise ValidationError("unsupported product acceptance manifest version")
    if evidence.get("schema_version") != "graph-harness.product-evidence.v1":
        raise ValidationError("unsupported product evidence version")
    product = manifest.get("product")
    capability = manifest.get("capability")
    if not all(isinstance(v, str) and v.strip() for v in (product, capability, source_revision)):
        raise ValidationError("product, capability and source revision are required")
    personas = _unique_strings(manifest.get("required_personas"), "required_personas")
    actions = manifest.get("critical_actions")
    workflows = manifest.get("workflows")
    if not isinstance(actions, list) or not actions or not isinstance(workflows, list) or not workflows:
        raise ValidationError("critical_actions and workflows must be populated")
    action_by_id: dict[str, dict[str, Any]] = {}
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get("id"), str) or not action["id"]:
            raise ValidationError("each action must have an id")
        if action["id"] in action_by_id:
            raise ValidationError(f"duplicate action {action['id']}")
        if action.get("persona") not in personas or not isinstance(action.get("outcome"), str) or not action["outcome"].strip():
            raise ValidationError(f"invalid persona/outcome for {action['id']}")
        if not isinstance(action.get("mutates_state"), bool):
            raise ValidationError(f"mutates_state must be bool for {action['id']}")
        action_by_id[action["id"]] = action

    blockers: list[str] = []
    action_coverage: dict[str, dict[str, str]] = {}
    workflow_coverage: dict[str, str] = {}
    action_workflows: set[str] = set()
    persona_workflows: set[str] = set()
    for workflow in workflows:
        if not isinstance(workflow, dict) or not isinstance(workflow.get("id"), str) or not workflow["id"]:
            raise ValidationError("workflows require unique ids")
        if workflow["id"] in workflow_coverage:
            raise ValidationError(f"duplicate workflow {workflow['id']}")
        persona = workflow.get("persona")
        if persona not in personas:
            raise ValidationError(f"workflow {workflow['id']} has unknown persona")
        action_ids = _unique_strings(workflow.get("actions"), f"workflow {workflow['id']}.actions")
        # A single page or route must never imply a full business workflow.
        if len(action_ids) < 2:
            blockers.append(f"workflow:{workflow['id']}:too_narrow")
        for action_id in action_ids:
            if action_id not in action_by_id:
                raise ValidationError(f"workflow {workflow['id']} references unknown action {action_id}")
            if action_by_id[action_id]["persona"] != persona:
                raise ValidationError(f"workflow {workflow['id']} role mismatch for {action_id}")
            action_workflows.add(action_id)
        persona_workflows.add(persona)
        workflow_coverage[workflow["id"]] = "covered" if len(action_ids) >= 2 else "too_narrow"
    for role in personas:
        if role not in persona_workflows:
            blockers.append(f"persona:{role}:missing_workflow")
    for action_id in action_by_id:
        if action_id not in action_workflows:
            blockers.append(f"action:{action_id}:not_in_workflow")

    proofs = evidence.get("proofs", [])
    if not isinstance(proofs, list):
        raise ValidationError("proofs must be array")
    proof_by_id: dict[str, dict[str, Any]] = {}
    for proof in proofs:
        if not isinstance(proof, dict) or not isinstance(proof.get("id"), str) or not proof["id"]:
            raise ValidationError("proof entries require ids")
        if proof["id"] in proof_by_id:
            raise ValidationError(f"duplicate proof {proof['id']}")
        proof_by_id[proof["id"]] = proof

    root = Path(repo_root).resolve()
    for action_id, action in action_by_id.items():
        covered: dict[str, str] = {}
        refs = action.get("proofs", {})
        if not isinstance(refs, dict):
            raise ValidationError(f"{action_id}.proofs must be object")
        for kind in KINDS:
            reason = "missing_proof"
            proof_id = refs.get(kind)
            proof = proof_by_id.get(proof_id) if isinstance(proof_id, str) else None
            if proof is not None:
                reason = _check_proof(proof, kind, action, root, source_revision, production_revision)
            covered[kind] = "PASS" if reason == "PASS" else reason
            if reason != "PASS":
                blockers.append(f"action:{action_id}:{kind}:{reason}")
        action_coverage[action_id] = covered

    approval_ref = manifest.get("coverage_approval")
    approval = proof_by_id.get(approval_ref) if isinstance(approval_ref, str) else None
    if approval is None:
        blockers.append("scope:missing_independent_coverage_approval")
    else:
        review = _check_proof(approval, "coverage_review", {"persona": "scope", "mutates_state": False}, root, source_revision, production_revision)
        reviewed_actions = approval.get("reviewed_actions", [])
        reviewed_personas = approval.get("reviewed_personas", [])
        if review == "PASS" and (
            not isinstance(reviewed_actions, list)
            or not isinstance(reviewed_personas, list)
            or any(not isinstance(value, str) for value in reviewed_actions + reviewed_personas)
            or set(reviewed_actions) != set(action_by_id)
            or set(reviewed_personas) != set(personas)
        ):
            review = "incomplete_scope_review"
        if review != "PASS":
            blockers.append(f"scope:{review}")
    if not production_revision:
        blockers.append("deployment:missing_independently_observed_revision")
    elif source_revision != production_revision:
        blockers.append("deployment:source_revision_differs_from_production")

    totals = {kind: sum(v[kind] == "PASS" for v in action_coverage.values()) for kind in KINDS}
    return {
        "schema_version": "graph-harness.acceptance-result.v1",
        "product": product,
        "capability": capability,
        "decision": "GO" if not blockers else "NO_GO",
        "source_revision": source_revision,
        "production_revision": production_revision,
        "required_actions": len(actions),
        "axis_pass_counts": totals,
        "workflows": workflow_coverage,
        "actions": action_coverage,
        "blockers": blockers,
    }


def _check_proof(
    proof: Mapping[str, Any],
    kind: str,
    action: Mapping[str, Any],
    root: Path,
    source_revision: str,
    production_revision: str | None,
) -> str:
    if proof.get("kind") != kind or proof.get("result") != "PASS":
        return "incorrect_kind_or_failed"
    if kind != "coverage_review" and proof.get("action_id") != action.get("id"):
        return "proof_does_not_identify_action"
    if proof.get("revision") != source_revision:
        return "stale_revision"
    if not _artifact_valid(proof, root):
        return "missing_or_invalid_artifact"
    if (not isinstance(proof.get("producer"), str) or not proof["producer"].strip()
        or not isinstance(proof.get("verifier"), str) or not proof["verifier"].strip()
        or proof["verifier"] == proof["producer"]):
        return "not_independently_verified"
    if kind in ("ui", "journey", "production"):
        mode = proof.get("mode", "")
        if not isinstance(mode, str) or not mode or any(term in mode.lower() for term in FORBIDDEN_MODES):
            return "synthetic_or_missing_mode"
    if kind == "ui" and (proof.get("role") != action["persona"] or proof.get("action_asserted") is not True):
        return "no_authenticated_action_assertion"
    if kind == "journey":
        if proof.get("role") != action["persona"] or proof.get("action_asserted") is not True:
            return "no_real_role_action"
        if action["mutates_state"] and proof.get("persisted_state_asserted") is not True:
            return "no_persisted_business_outcome"
        if proof.get("provider_connected") is not True:
            return "external_service_not_exercised"
    if kind == "production":
        if not production_revision or proof.get("revision") != production_revision or proof.get("environment") != "production":
            return "not_verified_on_deployed_revision"
        if proof.get("action_asserted") is not True or proof.get("role") != action["persona"]:
            return "production_action_not_exercised"
    if kind == "coverage_review" and proof.get("decision") != "APPROVED":
        return "scope_not_approved"
    return "PASS"


def evaluate_files(
    manifest_path: str | Path,
    evidence_path: str | Path,
    *,
    repo_root: str | Path,
    source_revision: str,
    production_revision: str | None = None,
) -> dict[str, Any]:
    return assess_product_acceptance(
        _read_json(manifest_path),
        _read_json(evidence_path),
        repo_root=repo_root,
        source_revision=source_revision,
        production_revision=production_revision,
    )
