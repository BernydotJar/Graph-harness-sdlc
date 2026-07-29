from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from graph_harness.model import GateResult, NodeStatus, ProjectDefinition, ValidationError
from graph_harness.runtime import GraphRuntime
from graph_harness.store import EventStore


def project_mapping() -> dict:
    return {
        "schema_version": "graph-harness.project.v1",
        "project_id": "test-project",
        "mode": "SHIP",
        "gate_definitions": [
            {"id": "spec", "required_evidence_kinds": ["spec"], "blocking": True},
            {"id": "verification", "required_evidence_kinds": ["test"], "blocking": True},
            {"id": "production", "required_evidence_kinds": ["security"], "blocking": True},
            {"id": "close", "required_evidence_kinds": ["review"], "blocking": True},
        ],
        "nodes": [
            {
                "id": "A",
                "kind": "feature",
                "title": "Root feature",
                "status": "spec_ready",
                "depends_on": [],
                "capability": "implementation",
                "gates": {
                    "approved": ["spec"],
                    "review": ["verification"],
                    "done": ["production", "close"],
                },
                "allowed_paths": ["src/**"],
            },
            {
                "id": "B",
                "kind": "feature",
                "title": "Dependent feature",
                "status": "approved",
                "depends_on": ["A"],
                "capability": "implementation",
                "gates": {},
                "allowed_paths": ["src/**"],
            },
            {
                "id": "C",
                "kind": "decision",
                "title": "Unrelated completed decision",
                "status": "done",
                "depends_on": [],
                "capability": "review",
                "gates": {},
                "allowed_paths": ["docs/**"],
            },
        ],
    }


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.project_path = root / "project.json"
        self.events_path = root / "events.jsonl"
        self.project_path.write_text(json.dumps(project_mapping()), encoding="utf-8")
        self.runtime = GraphRuntime.from_paths(self.project_path, self.events_path)

    def evidence(self, node: str, kind: str, artifact: str) -> str:
        event = self.runtime.record_evidence(
            node,
            actor="tester",
            kind=kind,
            result="PASS",
            artifact=artifact,
            sha256="a" * 64,
            command="unit-test",
            commit="deadbeef",
        )
        return event.event_id

    def complete_a(self) -> None:
        spec = self.evidence("A", "spec", "specs/A.md")
        self.runtime.evaluate_gate(
            "A", actor="reviewer", gate_id="spec", result=GateResult.PASS, evidence_ids=[spec], note="complete"
        )
        self.runtime.record_approval("A", actor="human", scope_hash="b" * 64, note="approved")
        self.runtime.transition("A", actor="leader", target=NodeStatus.APPROVED, reason="approved")
        self.runtime.transition("A", actor="leader", target=NodeStatus.READY, reason="dependencies satisfied")
        self.runtime.transition("A", actor="implementer", target=NodeStatus.RUNNING, reason="start")
        test = self.evidence("A", "test", "test.log")
        self.runtime.evaluate_gate(
            "A",
            actor="reviewer",
            gate_id="verification",
            result=GateResult.PASS,
            evidence_ids=[test],
            note="tests pass",
        )
        self.runtime.transition("A", actor="implementer", target=NodeStatus.REVIEW, reason="ready for review")
        security = self.evidence("A", "security", "security.md")
        review = self.evidence("A", "review", "review.md")
        self.runtime.evaluate_gate(
            "A",
            actor="production-reviewer",
            gate_id="production",
            result=GateResult.PASS,
            evidence_ids=[security],
            note="production gate passes",
        )
        self.runtime.evaluate_gate(
            "A", actor="reviewer", gate_id="close", result=GateResult.PASS, evidence_ids=[review], note="close"
        )
        self.runtime.transition("A", actor="human", target=NodeStatus.DONE, reason="closure approved")

    def test_validated_flow_exposes_ready_dependency(self) -> None:
        self.complete_a()
        state = self.runtime.state()
        self.assertEqual(NodeStatus.DONE, state.nodes["A"].status)
        self.assertEqual(["B"], self.runtime.ready_nodes())
        rendered = self.runtime.as_dict()
        self.assertEqual("graph-harness.state.v1", rendered["schema_version"])
        self.assertGreater(rendered["event_count"], 0)

    def test_gate_cannot_pass_without_required_evidence_kind(self) -> None:
        wrong = self.evidence("A", "test", "wrong.log")
        with self.assertRaisesRegex(ValidationError, "lacks evidence kinds"):
            self.runtime.evaluate_gate(
                "A", actor="reviewer", gate_id="spec", result=GateResult.PASS, evidence_ids=[wrong], note="bad"
            )

    def test_hash_chain_detects_tampering(self) -> None:
        self.evidence("A", "spec", "spec.md")
        lines = self.events_path.read_text(encoding="utf-8").splitlines()
        raw = json.loads(lines[0])
        raw["actor"] = "attacker"
        lines[0] = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        self.events_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "event_hash mismatch"):
            EventStore(self.events_path).load()

    def test_localized_repair_invalidates_only_descendants(self) -> None:
        self.complete_a()
        events = self.runtime.record_failure_and_plan_repair(
            "A", actor="reviewer", gate_id="production", reason="new security regression"
        )
        self.assertGreaterEqual(len(events), 4)
        state = self.runtime.state()
        self.assertEqual(NodeStatus.REPAIR_REQUIRED, state.nodes["A"].status)
        self.assertEqual(NodeStatus.REPAIR_REQUIRED, state.nodes["B"].status)
        self.assertEqual(NodeStatus.DONE, state.nodes["C"].status)
        self.assertEqual(1, state.nodes["A"].revision)
        self.assertEqual({}, state.nodes["A"].active_evidence())
        plan = state.repair_plans[-1].payload
        self.assertEqual(["A", "B"], plan["affected_nodes"])
        self.assertEqual(["C"], plan["preserved_nodes"])

    def test_cycle_is_rejected(self) -> None:
        raw = project_mapping()
        raw["nodes"][0]["depends_on"] = ["B"]
        with self.assertRaisesRegex(ValidationError, "dependency cycle"):
            ProjectDefinition.from_mapping(raw)

    def test_optimistic_append_rejects_stale_writer(self) -> None:
        first = self.runtime.checkpoint(actor="leader", label="one", commit="abc", evidence_summary={})
        with self.assertRaisesRegex(ValidationError, "changed concurrently"):
            self.runtime.checkpoint(
                actor="leader",
                label="two",
                commit="def",
                evidence_summary={},
                expected_last_event_id="not-the-last-event",
            )
        second = self.runtime.checkpoint(
            actor="leader",
            label="two",
            commit="def",
            evidence_summary={},
            expected_last_event_id=first.event_id,
        )
        self.assertEqual(2, second.sequence)


if __name__ == "__main__":
    unittest.main()
