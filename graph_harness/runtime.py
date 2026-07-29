from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from .model import EventType, GateResult, NodeDefinition, NodeStatus, ProjectDefinition, ValidationError
from .store import EventStore, StoredEvent


@dataclass
class EvidenceRecord:
    event_id: str
    kind: str
    result: str
    artifact: str
    sha256: str
    revision: int
    payload: Mapping[str, Any]


@dataclass
class GateEvaluation:
    event_id: str
    gate_id: str
    result: GateResult
    evidence_ids: tuple[str, ...]
    revision: int


@dataclass
class NodeState:
    definition: NodeDefinition
    status: NodeStatus
    revision: int = 0
    approvals: list[StoredEvent] = field(default_factory=list)
    evidence: dict[str, EvidenceRecord] = field(default_factory=dict)
    gates: dict[str, GateEvaluation] = field(default_factory=dict)
    failures: list[StoredEvent] = field(default_factory=list)
    last_event_id: str | None = None

    def active_evidence(self) -> dict[str, EvidenceRecord]:
        return {key: value for key, value in self.evidence.items() if value.revision == self.revision}

    def active_approvals(self) -> list[StoredEvent]:
        return [event for event in self.approvals if event.node_revision == self.revision]


@dataclass
class GraphState:
    project: ProjectDefinition
    nodes: dict[str, NodeState]
    events: list[StoredEvent]
    checkpoints: list[StoredEvent]
    repair_plans: list[StoredEvent]

    @property
    def last_event_id(self) -> str | None:
        return self.events[-1].event_id if self.events else None


_ALLOWED_TRANSITIONS: dict[NodeStatus, set[NodeStatus]] = {
    NodeStatus.PENDING: {NodeStatus.SPEC_READY, NodeStatus.BLOCKED, NodeStatus.SUPERSEDED},
    NodeStatus.SPEC_READY: {NodeStatus.APPROVED, NodeStatus.BLOCKED, NodeStatus.SUPERSEDED},
    NodeStatus.APPROVED: {NodeStatus.READY, NodeStatus.BLOCKED, NodeStatus.SUPERSEDED},
    NodeStatus.READY: {NodeStatus.RUNNING, NodeStatus.BLOCKED, NodeStatus.SUPERSEDED},
    NodeStatus.RUNNING: {NodeStatus.REVIEW, NodeStatus.BLOCKED, NodeStatus.REPAIR_REQUIRED},
    NodeStatus.REVIEW: {NodeStatus.DONE, NodeStatus.BLOCKED, NodeStatus.REPAIR_REQUIRED},
    NodeStatus.DONE: {NodeStatus.REPAIR_REQUIRED, NodeStatus.SUPERSEDED},
    NodeStatus.BLOCKED: {
        NodeStatus.PENDING,
        NodeStatus.SPEC_READY,
        NodeStatus.APPROVED,
        NodeStatus.READY,
        NodeStatus.REPAIR_REQUIRED,
        NodeStatus.SUPERSEDED,
    },
    NodeStatus.REPAIR_REQUIRED: {NodeStatus.READY, NodeStatus.RUNNING, NodeStatus.BLOCKED},
    NodeStatus.SUPERSEDED: set(),
}


class GraphRuntime:
    def __init__(self, project: ProjectDefinition, store: EventStore):
        self.project = project
        self.store = store

    @classmethod
    def from_paths(cls, project_path: str | Path, events_path: str | Path) -> "GraphRuntime":
        return cls(ProjectDefinition.from_path(project_path), EventStore(events_path))

    def state(self) -> GraphState:
        events = self.store.load()
        nodes = {
            node_id: NodeState(definition=node, status=node.status)
            for node_id, node in self.project.nodes.items()
        }
        checkpoints: list[StoredEvent] = []
        repair_plans: list[StoredEvent] = []
        seen_ids: set[str] = set()
        for event in events:
            if event.project_id != self.project.project_id:
                raise ValidationError(
                    f"event {event.event_id} belongs to {event.project_id!r}, expected {self.project.project_id!r}"
                )
            if event.event_id in seen_ids:
                raise ValidationError(f"duplicate event_id {event.event_id}")
            seen_ids.add(event.event_id)
            if event.event_type is EventType.CHECKPOINT_RECORDED:
                if event.node_id is not None:
                    raise ValidationError(f"checkpoint event {event.event_id} must not target a node")
                checkpoints.append(event)
                continue
            if event.event_type is EventType.REPAIR_PLAN_CREATED:
                repair_plans.append(event)
                continue
            if event.node_id is None or event.node_id not in nodes:
                raise ValidationError(f"event {event.event_id} targets unknown node {event.node_id!r}")
            node = nodes[event.node_id]
            self._apply_event(node, event)
            node.last_event_id = event.event_id
        return GraphState(
            project=self.project,
            nodes=nodes,
            events=events,
            checkpoints=checkpoints,
            repair_plans=repair_plans,
        )

    def ready_nodes(self) -> list[str]:
        state = self.state()
        ready: list[str] = []
        for node_id, node in sorted(state.nodes.items()):
            if node.status is not NodeStatus.APPROVED:
                continue
            if all(state.nodes[dependency].status is NodeStatus.DONE for dependency in node.definition.depends_on):
                self._assert_target_gates(node, NodeStatus.READY)
                ready.append(node_id)
        return ready

    def record_approval(
        self,
        node_id: str,
        *,
        actor: str,
        scope_hash: str,
        note: str,
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        state, node = self._node(node_id)
        if node.status is not NodeStatus.SPEC_READY:
            raise ValidationError(f"node {node_id} must be spec_ready before approval")
        if len(scope_hash) != 64 or any(character not in "0123456789abcdef" for character in scope_hash):
            raise ValidationError("scope_hash must be a lowercase SHA-256")
        return self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.APPROVAL_RECORDED,
            actor=actor,
            node_id=node_id,
            node_revision=node.revision,
            payload={"scope_hash": scope_hash, "note": note},
            expected_last_event_id=expected_last_event_id,
        )

    def record_evidence(
        self,
        node_id: str,
        *,
        actor: str,
        kind: str,
        result: str,
        artifact: str,
        sha256: str,
        command: str,
        commit: str,
        metadata: Mapping[str, Any] | None = None,
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        _state, node = self._node(node_id)
        for label, value in {
            "kind": kind,
            "result": result,
            "artifact": artifact,
            "sha256": sha256,
            "command": command,
            "commit": commit,
        }.items():
            if not value.strip():
                raise ValidationError(f"evidence {label} must be non-empty")
        if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
            raise ValidationError("evidence sha256 must be a lowercase SHA-256")
        return self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.EVIDENCE_RECORDED,
            actor=actor,
            node_id=node_id,
            node_revision=node.revision,
            payload={
                "kind": kind,
                "result": result,
                "artifact": artifact,
                "sha256": sha256,
                "command": command,
                "commit": commit,
                "metadata": dict(metadata or {}),
            },
            expected_last_event_id=expected_last_event_id,
        )

    def evaluate_gate(
        self,
        node_id: str,
        *,
        actor: str,
        gate_id: str,
        result: GateResult,
        evidence_ids: Iterable[str],
        note: str,
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        _state, node = self._node(node_id)
        gate = self.project.gate_definitions.get(gate_id)
        if gate is None:
            raise ValidationError(f"unknown gate {gate_id!r}")
        evidence_id_tuple = tuple(dict.fromkeys(evidence_ids))
        active = node.active_evidence()
        missing = sorted(set(evidence_id_tuple) - set(active))
        if missing:
            raise ValidationError(f"gate {gate_id!r} references missing or stale evidence {missing}")
        if result is GateResult.PASS:
            kinds = {active[evidence_id].kind for evidence_id in evidence_id_tuple}
            missing_kinds = sorted(set(gate.required_evidence_kinds) - kinds)
            if missing_kinds:
                raise ValidationError(f"gate {gate_id!r} lacks evidence kinds {missing_kinds}")
            failed = [
                evidence_id
                for evidence_id in evidence_id_tuple
                if active[evidence_id].result.upper() not in {"PASS", "SUCCESS"}
            ]
            if failed:
                raise ValidationError(f"gate {gate_id!r} cannot pass with failed evidence {failed}")
        return self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.GATE_EVALUATED,
            actor=actor,
            node_id=node_id,
            node_revision=node.revision,
            payload={
                "gate_id": gate_id,
                "result": result.value,
                "evidence_ids": list(evidence_id_tuple),
                "note": note,
            },
            expected_last_event_id=expected_last_event_id,
        )

    def transition(
        self,
        node_id: str,
        *,
        actor: str,
        target: NodeStatus,
        reason: str,
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        state, node = self._node(node_id)
        if target not in _ALLOWED_TRANSITIONS[node.status]:
            raise ValidationError(f"invalid transition for {node_id}: {node.status.value} -> {target.value}")
        if target is NodeStatus.APPROVED and not node.active_approvals():
            raise ValidationError(f"node {node_id} requires current-revision human approval")
        if target is NodeStatus.READY:
            incomplete = [
                dependency
                for dependency in node.definition.depends_on
                if state.nodes[dependency].status is not NodeStatus.DONE
            ]
            if incomplete:
                raise ValidationError(f"node {node_id} has incomplete dependencies {incomplete}")
        self._assert_target_gates(node, target)
        return self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.NODE_TRANSITIONED,
            actor=actor,
            node_id=node_id,
            node_revision=node.revision,
            payload={"from": node.status.value, "to": target.value, "reason": reason},
            expected_last_event_id=expected_last_event_id,
        )

    def record_failure_and_plan_repair(
        self,
        node_id: str,
        *,
        actor: str,
        gate_id: str,
        reason: str,
        expected_last_event_id: str | None = None,
    ) -> list[StoredEvent]:
        state, node = self._node(node_id)
        if gate_id not in self.project.gate_definitions:
            raise ValidationError(f"unknown gate {gate_id!r}")
        written: list[StoredEvent] = []
        failure = self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.FAILURE_RECORDED,
            actor=actor,
            node_id=node_id,
            node_revision=node.revision,
            payload={"gate_id": gate_id, "reason": reason},
            expected_last_event_id=expected_last_event_id,
        )
        written.append(failure)
        affected = self._descendants(node_id)
        affected.add(node_id)
        latest_state = self.state()
        for affected_id in sorted(affected):
            affected_node = latest_state.nodes[affected_id]
            if affected_node.status in {NodeStatus.PENDING, NodeStatus.SPEC_READY, NodeStatus.SUPERSEDED}:
                continue
            invalidated = self.store.append(
                project_id=self.project.project_id,
                event_type=EventType.NODE_INVALIDATED,
                actor=actor,
                node_id=affected_id,
                node_revision=affected_node.revision,
                payload={
                    "failure_event_id": failure.event_id,
                    "source_node_id": node_id,
                    "reason": reason,
                },
            )
            written.append(invalidated)
            latest_state = self.state()
        plan = self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.REPAIR_PLAN_CREATED,
            actor=actor,
            payload={
                "failure_event_id": failure.event_id,
                "source_node_id": node_id,
                "affected_nodes": sorted(affected),
                "preserved_nodes": sorted(set(self.project.nodes) - affected),
            },
        )
        written.append(plan)
        return written

    def checkpoint(
        self,
        *,
        actor: str,
        label: str,
        commit: str,
        evidence_summary: Mapping[str, Any],
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        if not label.strip() or not commit.strip():
            raise ValidationError("checkpoint label and commit must be non-empty")
        return self.store.append(
            project_id=self.project.project_id,
            event_type=EventType.CHECKPOINT_RECORDED,
            actor=actor,
            payload={"label": label, "commit": commit, "evidence_summary": dict(evidence_summary)},
            expected_last_event_id=expected_last_event_id,
        )

    def as_dict(self) -> dict[str, Any]:
        state = self.state()
        return {
            "schema_version": "graph-harness.state.v1",
            "project_id": self.project.project_id,
            "mode": self.project.mode,
            "last_event_id": state.last_event_id,
            "event_count": len(state.events),
            "ready_nodes": self.ready_nodes(),
            "nodes": [
                {
                    "id": node_id,
                    "kind": node.definition.kind,
                    "title": node.definition.title,
                    "status": node.status.value,
                    "revision": node.revision,
                    "depends_on": list(node.definition.depends_on),
                    "capability": node.definition.capability,
                    "active_gates": {
                        gate_id: evaluation.result.value
                        for gate_id, evaluation in sorted(node.gates.items())
                        if evaluation.revision == node.revision
                    },
                    "active_evidence_ids": sorted(node.active_evidence()),
                    "approval_count": len(node.active_approvals()),
                }
                for node_id, node in sorted(state.nodes.items())
            ],
            "checkpoint_count": len(state.checkpoints),
            "repair_plan_count": len(state.repair_plans),
        }

    def _node(self, node_id: str) -> tuple[GraphState, NodeState]:
        state = self.state()
        try:
            return state, state.nodes[node_id]
        except KeyError as error:
            raise ValidationError(f"unknown node {node_id!r}") from error

    def _assert_target_gates(self, node: NodeState, target: NodeStatus) -> None:
        required = node.definition.gates.get(target.value, ())
        missing: list[str] = []
        for gate_id in required:
            evaluation = node.gates.get(gate_id)
            if (
                evaluation is None
                or evaluation.revision != node.revision
                or evaluation.result is not GateResult.PASS
            ):
                missing.append(gate_id)
        if missing:
            raise ValidationError(
                f"node {node.definition.id} cannot enter {target.value}; gates not passing: {missing}"
            )

    def _apply_event(self, node: NodeState, event: StoredEvent) -> None:
        if event.node_revision != node.revision:
            raise ValidationError(
                f"event {event.event_id} revision {event.node_revision} does not match "
                f"node {node.definition.id} revision {node.revision}"
            )
        payload = event.payload
        if event.event_type is EventType.APPROVAL_RECORDED:
            node.approvals.append(event)
        elif event.event_type is EventType.EVIDENCE_RECORDED:
            required = ("kind", "result", "artifact", "sha256", "command", "commit")
            if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
                raise ValidationError(f"evidence event {event.event_id} is incomplete")
            node.evidence[event.event_id] = EvidenceRecord(
                event_id=event.event_id,
                kind=payload["kind"],
                result=payload["result"],
                artifact=payload["artifact"],
                sha256=payload["sha256"],
                revision=node.revision,
                payload=payload,
            )
        elif event.event_type is EventType.GATE_EVALUATED:
            gate_id = payload.get("gate_id")
            if gate_id not in self.project.gate_definitions:
                raise ValidationError(f"gate event {event.event_id} references unknown gate")
            try:
                result = GateResult(payload.get("result"))
            except ValueError as error:
                raise ValidationError(f"gate event {event.event_id} has invalid result") from error
            evidence_ids = payload.get("evidence_ids")
            if not isinstance(evidence_ids, list) or not all(isinstance(item, str) for item in evidence_ids):
                raise ValidationError(f"gate event {event.event_id} evidence_ids must be strings")
            unknown = sorted(set(evidence_ids) - set(node.active_evidence()))
            if unknown:
                raise ValidationError(f"gate event {event.event_id} references stale evidence {unknown}")
            node.gates[gate_id] = GateEvaluation(
                event_id=event.event_id,
                gate_id=gate_id,
                result=result,
                evidence_ids=tuple(evidence_ids),
                revision=node.revision,
            )
        elif event.event_type is EventType.NODE_TRANSITIONED:
            try:
                source = NodeStatus(payload.get("from"))
                target = NodeStatus(payload.get("to"))
            except ValueError as error:
                raise ValidationError(f"transition event {event.event_id} has invalid status") from error
            if source is not node.status:
                raise ValidationError(
                    f"transition event {event.event_id} expected {source.value}, node is {node.status.value}"
                )
            if target not in _ALLOWED_TRANSITIONS[source]:
                raise ValidationError(f"transition event {event.event_id} is not allowed")
            node.status = target
        elif event.event_type is EventType.FAILURE_RECORDED:
            node.failures.append(event)
        elif event.event_type is EventType.NODE_INVALIDATED:
            node.revision += 1
            node.status = NodeStatus.REPAIR_REQUIRED
        else:
            raise ValidationError(f"event {event.event_id} cannot target a node")

    def _descendants(self, node_id: str) -> set[str]:
        descendants: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for candidate in self.project.nodes.values():
                if current in candidate.depends_on and candidate.id not in descendants:
                    descendants.add(candidate.id)
                    frontier.append(candidate.id)
        return descendants
