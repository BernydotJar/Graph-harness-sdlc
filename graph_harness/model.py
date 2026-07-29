from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a graph, event, transition, or gate is invalid."""


class NodeStatus(str, Enum):
    PENDING = "pending"
    SPEC_READY = "spec_ready"
    APPROVED = "approved"
    READY = "ready"
    RUNNING = "running"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"
    REPAIR_REQUIRED = "repair_required"
    SUPERSEDED = "superseded"


class GateResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class EventType(str, Enum):
    APPROVAL_RECORDED = "approval.recorded"
    EVIDENCE_RECORDED = "evidence.recorded"
    GATE_EVALUATED = "gate.evaluated"
    NODE_TRANSITIONED = "node.transitioned"
    FAILURE_RECORDED = "failure.recorded"
    NODE_INVALIDATED = "node.invalidated"
    REPAIR_PLAN_CREATED = "repair.plan_created"
    CHECKPOINT_RECORDED = "checkpoint.recorded"


@dataclass(frozen=True)
class GateDefinition:
    id: str
    required_evidence_kinds: tuple[str, ...] = ()
    blocking: bool = True


@dataclass(frozen=True)
class NodeDefinition:
    id: str
    kind: str
    title: str
    status: NodeStatus
    depends_on: tuple[str, ...] = ()
    capability: str = "general"
    gates: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    allowed_paths: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectDefinition:
    schema_version: str
    project_id: str
    mode: str
    nodes: Mapping[str, NodeDefinition]
    gate_definitions: Mapping[str, GateDefinition]

    @classmethod
    def from_path(cls, path: str | Path) -> "ProjectDefinition":
        project_path = Path(path)
        try:
            raw = json.loads(project_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValidationError(f"{project_path}: invalid project JSON: {error}") from error
        if not isinstance(raw, Mapping):
            raise ValidationError(f"{project_path}: project root must be an object")
        return cls.from_mapping(raw)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProjectDefinition":
        schema_version = raw.get("schema_version")
        if schema_version != "graph-harness.project.v1":
            raise ValidationError("project.schema_version must be graph-harness.project.v1")
        project_id = _required_string(raw, "project_id", "project")
        mode = _required_string(raw, "mode", "project").upper()
        if mode not in {"MVP", "SHIP"}:
            raise ValidationError("project.mode must be MVP or SHIP")

        raw_gates = raw.get("gate_definitions")
        if not isinstance(raw_gates, list) or not raw_gates:
            raise ValidationError("project.gate_definitions must be a non-empty array")
        gate_definitions: dict[str, GateDefinition] = {}
        for index, item in enumerate(raw_gates):
            if not isinstance(item, Mapping):
                raise ValidationError(f"gate_definitions[{index}] must be an object")
            gate_id = _required_string(item, "id", f"gate_definitions[{index}]")
            if gate_id in gate_definitions:
                raise ValidationError(f"duplicate gate definition {gate_id!r}")
            kinds = item.get("required_evidence_kinds", [])
            if not _is_string_list(kinds):
                raise ValidationError(
                    f"gate_definitions[{index}].required_evidence_kinds must be strings"
                )
            blocking = item.get("blocking", True)
            if not isinstance(blocking, bool):
                raise ValidationError(f"gate_definitions[{index}].blocking must be boolean")
            gate_definitions[gate_id] = GateDefinition(
                id=gate_id,
                required_evidence_kinds=tuple(kinds),
                blocking=blocking,
            )

        raw_nodes = raw.get("nodes")
        if not isinstance(raw_nodes, list) or not raw_nodes:
            raise ValidationError("project.nodes must be a non-empty array")
        nodes: dict[str, NodeDefinition] = {}
        for index, item in enumerate(raw_nodes):
            if not isinstance(item, Mapping):
                raise ValidationError(f"nodes[{index}] must be an object")
            node_id = _required_string(item, "id", f"nodes[{index}]")
            if node_id in nodes:
                raise ValidationError(f"duplicate node {node_id!r}")
            try:
                status = NodeStatus(_required_string(item, "status", f"nodes[{index}]"))
            except ValueError as error:
                raise ValidationError(f"nodes[{index}].status is invalid") from error
            depends_on = item.get("depends_on", [])
            allowed_paths = item.get("allowed_paths", [])
            if not _is_string_list(depends_on):
                raise ValidationError(f"nodes[{index}].depends_on must be strings")
            if not _is_string_list(allowed_paths):
                raise ValidationError(f"nodes[{index}].allowed_paths must be strings")
            gates_raw = item.get("gates", {})
            if not isinstance(gates_raw, Mapping):
                raise ValidationError(f"nodes[{index}].gates must be an object")
            gates: dict[str, tuple[str, ...]] = {}
            for target, gate_ids in gates_raw.items():
                if target not in {status.value for status in NodeStatus}:
                    raise ValidationError(
                        f"nodes[{index}].gates target {target!r} is not a node status"
                    )
                if not _is_string_list(gate_ids):
                    raise ValidationError(
                        f"nodes[{index}].gates.{target} must be an array of strings"
                    )
                unknown_gates = sorted(set(gate_ids) - set(gate_definitions))
                if unknown_gates:
                    raise ValidationError(
                        f"nodes[{index}].gates.{target} references unknown gates {unknown_gates}"
                    )
                gates[target] = tuple(gate_ids)
            metadata = item.get("metadata", {})
            if not isinstance(metadata, Mapping):
                raise ValidationError(f"nodes[{index}].metadata must be an object")
            nodes[node_id] = NodeDefinition(
                id=node_id,
                kind=_required_string(item, "kind", f"nodes[{index}]"),
                title=_required_string(item, "title", f"nodes[{index}]"),
                status=status,
                depends_on=tuple(depends_on),
                capability=str(item.get("capability") or "general"),
                gates=gates,
                allowed_paths=tuple(allowed_paths),
                metadata=dict(metadata),
            )

        node_ids = set(nodes)
        for node in nodes.values():
            unknown = sorted(set(node.depends_on) - node_ids)
            if unknown:
                raise ValidationError(f"node {node.id!r} depends on unknown nodes {unknown}")
            if node.id in node.depends_on:
                raise ValidationError(f"node {node.id!r} depends on itself")
        _validate_acyclic(nodes)
        return cls(
            schema_version=schema_version,
            project_id=project_id,
            mode=mode,
            nodes=nodes,
            gate_definitions=gate_definitions,
        )


def _required_string(item: Mapping[str, Any], key: str, label: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label}.{key} must be a non-empty string")
    return value.strip()


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _validate_acyclic(nodes: Mapping[str, NodeDefinition]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str, path: tuple[str, ...]) -> None:
        if node_id in visiting:
            raise ValidationError("dependency cycle: " + " -> ".join((*path, node_id)))
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in nodes[node_id].depends_on:
            visit(dependency, (*path, node_id))
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(nodes):
        visit(node_id, ())
