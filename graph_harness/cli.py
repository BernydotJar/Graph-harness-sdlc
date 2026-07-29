from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .model import GateResult, NodeStatus, ValidationError
from .runtime import GraphRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graph-harness")
    parser.add_argument("--project", required=True, help="Path to graph-harness.project.v1 JSON")
    parser.add_argument("--events", required=True, help="Path to append-only event JSONL")
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


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runtime = GraphRuntime.from_paths(args.project, args.events)
        if args.command == "validate":
            state = runtime.as_dict()
            print(
                json.dumps(
                    {
                        "valid": True,
                        "project_id": state["project_id"],
                        "event_count": state["event_count"],
                        "ready_nodes": state["ready_nodes"],
                    },
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "status":
            print(json.dumps(runtime.as_dict(), indent=2 if args.pretty else None, sort_keys=True))
            return 0
        if args.command == "ready":
            print(json.dumps({"ready_nodes": runtime.ready_nodes()}, indent=2 if args.pretty else None))
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
            print(json.dumps({"event_ids": [event.event_id for event in events]}, sort_keys=True))
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
            raise AssertionError(f"unhandled command {args.command}")
        print(json.dumps(event.as_dict(), sort_keys=True))
        return 0
    except ValidationError as error:
        print(f"graph-harness: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
