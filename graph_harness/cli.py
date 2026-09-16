from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .bootstrap import apply_bootstrap, run_preflight
from .doctor import run_doctor
from .model import GateResult, NodeStatus, ValidationError
from .policy import ActionRequest, Decision, PolicyLayer, evaluate_action, resolve_policy
from .profiles import DeveloperProfile
from .providers import get_provider_adapter, provider_ids
from .runtime import GraphRuntime
from .skills import SkillRegistry
from .telemetry import AttributionContext

_RUNTIME_COMMANDS = {
    "validate",
    "status",
    "ready",
    "record-approval",
    "record-evidence",
    "evaluate-gate",
    "transition",
    "fail",
    "checkpoint",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graph-harness")
    parser.add_argument("--project", help="Path to graph-harness.project.v1 JSON for runtime commands")
    parser.add_argument("--events", help="Path to append-only event JSONL for runtime commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate project, event chain, and projected state")
    status = subparsers.add_parser("status", help="Render typed graph state")
    status.add_argument("--pretty", action="store_true")
    ready = subparsers.add_parser("ready", help="List executable nodes")
    ready.add_argument("--pretty", action="store_true")

    approval = subparsers.add_parser("record-approval", help="Record explicit human approval")
    _node_actor_arguments(approval)
    approval.add_argument("--scope-hash", required=True)
    approval.add_argument("--note", required=True)

    evidence = subparsers.add_parser("record-evidence", help="Append persistent evidence")
    _node_actor_arguments(evidence)
    evidence.add_argument("--kind", required=True)
    evidence.add_argument("--result", required=True)
    evidence.add_argument("--artifact", required=True)
    evidence.add_argument("--sha256")
    evidence.add_argument("--command-line", required=True)
    evidence.add_argument("--commit", required=True)
    evidence.add_argument("--metadata-json", default="{}")

    gate = subparsers.add_parser("evaluate-gate", help="Evaluate a gate from evidence")
    _node_actor_arguments(gate)
    gate.add_argument("--gate", required=True)
    gate.add_argument("--result", choices=[item.value for item in GateResult], required=True)
    gate.add_argument("--evidence", nargs="*", default=[])
    gate.add_argument("--note", required=True)

    transition = subparsers.add_parser("transition", help="Apply a validated state transition")
    _node_actor_arguments(transition)
    transition.add_argument("--to", choices=[item.value for item in NodeStatus], required=True)
    transition.add_argument("--reason", required=True)

    failure = subparsers.add_parser("fail", help="Record a failure and localized repair plan")
    _node_actor_arguments(failure)
    failure.add_argument("--gate", required=True)
    failure.add_argument("--reason", required=True)

    checkpoint = subparsers.add_parser("checkpoint", help="Record a project checkpoint")
    checkpoint.add_argument("--actor", required=True)
    checkpoint.add_argument("--label", required=True)
    checkpoint.add_argument("--commit", required=True)
    checkpoint.add_argument("--summary-json", default="{}")
    checkpoint.add_argument("--expected-last-event-id")

    policy = subparsers.add_parser("policy-resolve", help="Resolve hierarchical policy layers")
    policy.add_argument("--layer", action="append", required=True, help="Policy JSON; pass broad to specific")
    policy.add_argument("--profile", help="Optional lowest-precedence developer preference profile")
    policy.add_argument("--pretty", action="store_true")

    action = subparsers.add_parser("check-action", help="Evaluate an action before execution")
    action.add_argument("--layer", action="append", default=[], help="Policy JSON; pass broad to specific")
    action.add_argument("--profile", help="Optional developer preference profile")
    action.add_argument("--kind", default="generic")
    action.add_argument("--command-line", default="")
    action.add_argument("--path", action="append", default=[])
    action.add_argument("--content-file")
    action.add_argument("--approved", action="store_true")
    action.add_argument("--pretty", action="store_true")

    preflight = subparsers.add_parser("preflight", help="Read-only identity and environment preflight")
    preflight.add_argument("--root", default=".")
    preflight.add_argument("--expect")
    preflight.add_argument("--require-command", action="append", default=[])
    preflight.add_argument("--pretty", action="store_true")

    bootstrap = subparsers.add_parser("bootstrap", help="Plan or apply non-destructive control-plane scaffolding")
    bootstrap.add_argument("--root", default=".")
    bootstrap_mode = bootstrap.add_mutually_exclusive_group()
    bootstrap_mode.add_argument("--dry-run", action="store_true", help="Preview only; this is the default")
    bootstrap_mode.add_argument("--apply", action="store_true", help="Create missing files without overwriting existing files")
    bootstrap.add_argument("--pretty", action="store_true")

    provider = subparsers.add_parser("provider-render", help="Plan or apply a coding-agent instruction projection")
    provider.add_argument("--provider", required=True, choices=provider_ids())
    provider.add_argument("--root", required=True, help="Explicit target root; no home directory is assumed")
    provider.add_argument("--shared-file", required=True)
    provider.add_argument("--delta-file")
    provider.add_argument("--profile")
    provider.add_argument("--manifest-root", default=".")
    provider_mode = provider.add_mutually_exclusive_group()
    provider_mode.add_argument("--dry-run", action="store_true", help="Preview only; this is the default")
    provider_mode.add_argument("--apply", action="store_true")
    provider.add_argument("--pretty", action="store_true")

    doctor = subparsers.add_parser("doctor", help="Read-only control-plane and projection drift checks")
    doctor.add_argument("--root", default=".")
    doctor.add_argument("--expect")
    doctor.add_argument("--pretty", action="store_true")

    skills = subparsers.add_parser("skills", help="Validate and inspect the skill lifecycle registry")
    skills.add_argument("--registry", default="skills/registry.json")
    skills.add_argument("--status", choices=["stable", "experimental"])
    skills.add_argument("--pretty", action="store_true")

    attribution = subparsers.add_parser("attribution", help="Render local provider-neutral execution attribution")
    attribution.add_argument("--config", required=True)
    attribution.add_argument("--pretty", action="store_true")
    return parser


def _node_actor_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--node", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--expected-last-event-id")


def _json_object(value: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValidationError(f"{label} is not valid JSON: {error}") from error
    if not isinstance(parsed, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return parsed


def _artifact_sha256(path_or_label: str) -> str:
    path = Path(path_or_label)
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    return hashlib.sha256(path_or_label.encode("utf-8")).hexdigest()


def _print_json(value: Any, *, pretty: bool = False) -> None:
    print(json.dumps(value, indent=2 if pretty else None, sort_keys=True))


def _load_policy(layer_paths: list[str], profile_path: str | None):
    layers = [PolicyLayer.from_path(path) for path in layer_paths]
    preferences = None
    if profile_path:
        preferences = dict(DeveloperProfile.from_path(profile_path).preferences)
    return resolve_policy(layers, profile_preferences=preferences)


def _runtime(args: argparse.Namespace) -> GraphRuntime:
    if not args.project or not args.events:
        raise ValidationError(f"{args.command} requires both --project and --events")
    return GraphRuntime.from_paths(args.project, args.events)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in _RUNTIME_COMMANDS:
            return _handle_runtime(args)
        if args.command == "policy-resolve":
            policy = _load_policy(args.layer, args.profile)
            _print_json(policy.as_dict(), pretty=args.pretty)
            return 0
        if args.command == "check-action":
            policy = _load_policy(args.layer, args.profile)
            content = ""
            if args.content_file:
                content = Path(args.content_file).read_text(encoding="utf-8")
            evaluation = evaluate_action(
                policy,
                ActionRequest(
                    kind=args.kind,
                    command=args.command_line,
                    paths=tuple(args.path),
                    content=content,
                    approved=args.approved,
                ),
            )
            _print_json(evaluation.as_dict(), pretty=args.pretty)
            return 3 if evaluation.decision is Decision.DENY else 0
        if args.command == "preflight":
            result = run_preflight(
                args.root,
                expectations_path=args.expect,
                require_commands=tuple(args.require_command),
            )
            _print_json(result.as_dict(), pretty=args.pretty)
            return 0 if result.ok else 2
        if args.command == "bootstrap":
            dry_run = not args.apply
            plan = apply_bootstrap(args.root, dry_run=dry_run)
            payload = plan.as_dict()
            payload["dry_run"] = dry_run
            _print_json(payload, pretty=args.pretty)
            return 0
        if args.command == "provider-render":
            adapter = get_provider_adapter(args.provider)
            shared_text = Path(args.shared_file).read_text(encoding="utf-8")
            delta_text = Path(args.delta_file).read_text(encoding="utf-8") if args.delta_file else ""
            preferences: dict[str, Any] = {}
            if args.profile:
                preferences = dict(DeveloperProfile.from_path(args.profile).preferences)
            sources = {"shared": args.shared_file}
            if args.delta_file:
                sources["delta"] = args.delta_file
            if args.profile:
                sources["profile"] = args.profile
            if args.apply:
                plan = adapter.apply(
                    target_root=args.root,
                    shared_text=shared_text,
                    provider_delta=delta_text,
                    preferences=preferences,
                    manifest_root=args.manifest_root,
                    sources=sources,
                )
            else:
                plan = adapter.plan(
                    target_root=args.root,
                    shared_text=shared_text,
                    provider_delta=delta_text,
                    preferences=preferences,
                )
            payload = plan.as_dict()
            payload["dry_run"] = not args.apply
            payload["applied"] = bool(args.apply)
            _print_json(payload, pretty=args.pretty)
            return 0
        if args.command == "doctor":
            report = run_doctor(args.root, expectations_path=args.expect)
            _print_json(report.as_dict(), pretty=args.pretty)
            return 0 if report.ok else 2
        if args.command == "skills":
            registry = SkillRegistry.from_path(args.registry)
            _print_json(registry.as_dict(status=args.status), pretty=args.pretty)
            return 0
        if args.command == "attribution":
            attribution = AttributionContext.from_path(args.config)
            _print_json(attribution.as_dict(), pretty=args.pretty)
            return 0
        raise AssertionError(f"unhandled command {args.command}")
    except (ValidationError, OSError) as error:
        print(f"graph-harness: {error}", file=sys.stderr)
        return 2


def _handle_runtime(args: argparse.Namespace) -> int:
    runtime = _runtime(args)
    if args.command == "validate":
        state = runtime.as_dict()
        _print_json(
            {
                "valid": True,
                "project_id": state["project_id"],
                "event_count": state["event_count"],
                "ready_nodes": state["ready_nodes"],
            }
        )
        return 0
    if args.command == "status":
        _print_json(runtime.as_dict(), pretty=args.pretty)
        return 0
    if args.command == "ready":
        _print_json({"ready_nodes": runtime.ready_nodes()}, pretty=args.pretty)
        return 0
    if args.command == "record-approval":
        event = runtime.record_approval(
            args.node,
            actor=args.actor,
            scope_hash=args.scope_hash,
            note=args.note,
            expected_last_event_id=args.expected_last_event_id,
        )
    elif args.command == "record-evidence":
        metadata = _json_object(args.metadata_json, "metadata-json")
        evidence_hash = args.sha256 or _artifact_sha256(args.artifact)
        event = runtime.record_evidence(
            args.node,
            actor=args.actor,
            kind=args.kind,
            result=args.result,
            artifact=args.artifact,
            sha256=evidence_hash,
            command=args.command_line,
            commit=args.commit,
            metadata=metadata,
            expected_last_event_id=args.expected_last_event_id,
        )
    elif args.command == "evaluate-gate":
        event = runtime.evaluate_gate(
            args.node,
            actor=args.actor,
            gate_id=args.gate,
            result=GateResult(args.result),
            evidence_ids=args.evidence,
            note=args.note,
            expected_last_event_id=args.expected_last_event_id,
        )
    elif args.command == "transition":
        event = runtime.transition(
            args.node,
            actor=args.actor,
            target=NodeStatus(args.to),
            reason=args.reason,
            expected_last_event_id=args.expected_last_event_id,
        )
    elif args.command == "fail":
        events = runtime.record_failure_and_plan_repair(
            args.node,
            actor=args.actor,
            gate_id=args.gate,
            reason=args.reason,
            expected_last_event_id=args.expected_last_event_id,
        )
        _print_json({"event_ids": [event.event_id for event in events]})
        return 0
    elif args.command == "checkpoint":
        event = runtime.checkpoint(
            actor=args.actor,
            label=args.label,
            commit=args.commit,
            evidence_summary=_json_object(args.summary_json, "summary-json"),
            expected_last_event_id=args.expected_last_event_id,
        )
    else:
        raise AssertionError(f"unhandled runtime command {args.command}")
    _print_json(event.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
