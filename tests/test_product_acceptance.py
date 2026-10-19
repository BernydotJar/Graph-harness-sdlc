from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from graph_harness.cli import main
from graph_harness.model import ValidationError
from graph_harness.product_acceptance import assess_product_acceptance


class ProductAcceptanceTests(unittest.TestCase):
    SHA = "a" * 40

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.artifact = self.root / "evidence.json"
        self.artifact.write_text('{"checked":true}', encoding="utf-8")
        self.digest = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.manifest = {
            "schema_version": "graph-harness.product-acceptance.v1",
            "product": "LUMA", "capability": "Live classroom",
            "required_personas": ["instructor", "learner"],
            "critical_actions": [
                {"id": a, "persona": role, "outcome": "actual customer action", "mutates_state": mutates,
                 "proofs": {kind: f"{a}:{kind}" for kind in ("implementation", "ui", "journey", "production")}}
                for a, role, mutates in (("schedule", "instructor", True), ("close", "instructor", True),
                                        ("join", "learner", True), ("leave", "learner", False))
            ],
            "workflows": [
                {"id": "instructor-flow", "persona": "instructor", "actions": ["schedule", "close"]},
                {"id": "learner-flow", "persona": "learner", "actions": ["join", "leave"]},
            ],
            "coverage_approval": "scope-review",
        }
        proofs = []
        for action in self.manifest["critical_actions"]:
            for kind in ("implementation", "ui", "journey", "production"):
                proofs.append({
                    "id": f"{action['id']}:{kind}", "action_id": action["id"], "kind": kind,
                    "result": "PASS", "revision": self.SHA, "artifact": "evidence.json", "sha256": self.digest,
                    "producer": "author", "verifier": "independent-qa", "mode": "live-provider",
                    "role": action["persona"], "action_asserted": True,
                    "persisted_state_asserted": True, "provider_connected": True,
                    "environment": "production",
                })
        proofs.append({
            "id": "scope-review", "kind": "coverage_review", "result": "PASS", "revision": self.SHA,
            "artifact": "evidence.json", "sha256": self.digest,
            "producer": "author", "verifier": "client-qa", "decision": "APPROVED",
            "reviewed_actions": [a["id"] for a in self.manifest["critical_actions"]],
            "reviewed_personas": self.manifest["required_personas"],
        })
        self.evidence = {"schema_version": "graph-harness.product-evidence.v1", "proofs": proofs}

    def assess(self, prod_revision: str | None = None):
        return assess_product_acceptance(self.manifest, self.evidence, repo_root=self.root,
                                         source_revision=self.SHA, production_revision=prod_revision)

    def test_all_axes_real_actions_independent_review_and_same_deployment_can_go(self):
        self.assertEqual("GO", self.assess(self.SHA)["decision"])

    def test_missing_proofs_is_not_a_complete_module(self):
        self.evidence["proofs"] = []
        report = self.assess(self.SHA)
        self.assertEqual("NO_GO", report["decision"])
        self.assertEqual({"implementation": 0, "ui": 0, "journey": 0, "production": 0},
                         report["axis_pass_counts"])

    def test_a_green_e2e_and_screenshot_cannot_bypass_production(self):
        self.assertIn("deployment:missing_independently_observed_revision", self.assess()["blockers"])
        self.assertIn("deployment:source_revision_differs_from_production", self.assess("b"*40)["blockers"])

    def test_a_fixture_or_mocked_user_journey_does_not_count(self):
        self.evidence["proofs"][2]["mode"] = "synthetic emulators"
        self.assertIn("action:schedule:journey:synthetic_or_missing_mode", self.assess(self.SHA)["blockers"])

    def test_unverified_ui_click_rejects_data_only_screen(self):
        self.evidence["proofs"][1]["action_asserted"] = False
        self.assertIn("action:schedule:ui:no_authenticated_action_assertion", self.assess(self.SHA)["blockers"])

    def test_no_persisted_effect_rejects_click_only_e2e(self):
        self.evidence["proofs"][2]["persisted_state_asserted"] = False
        self.assertIn("action:schedule:journey:no_persisted_business_outcome", self.assess(self.SHA)["blockers"])

    def test_cross_action_proof_reuse_is_rejected(self):
        self.manifest["critical_actions"][1]["proofs"]["ui"] = "schedule:ui"
        self.assertIn("action:close:ui:proof_does_not_identify_action", self.assess(self.SHA)["blockers"])

    def test_one_page_is_not_a_customer_workflow(self):
        self.manifest["workflows"][0]["actions"] = ["schedule"]
        self.assertIn("workflow:instructor-flow:too_narrow", self.assess(self.SHA)["blockers"])
        self.assertIn("action:close:not_in_workflow", self.assess(self.SHA)["blockers"])

    def test_missing_role_and_unreviewed_actions_block(self):
        self.manifest["workflows"] = self.manifest["workflows"][:1]
        self.assertIn("persona:learner:missing_workflow", self.assess(self.SHA)["blockers"])
        self.evidence["proofs"][-1]["reviewed_actions"] = ["schedule"]
        self.assertIn("scope:incomplete_scope_review", self.assess(self.SHA)["blockers"])

    def test_self_review_stale_artifact_and_path_escape_block(self):
        self.evidence["proofs"][0]["verifier"] = "author"
        self.assertIn("action:schedule:implementation:not_independently_verified", self.assess(self.SHA)["blockers"])
        self.evidence["proofs"][0]["verifier"] = "ci"
        self.evidence["proofs"][0]["sha256"] = "0"*64
        self.assertIn("action:schedule:implementation:missing_or_invalid_artifact", self.assess(self.SHA)["blockers"])
        self.evidence["proofs"][0]["sha256"] = self.digest
        self.evidence["proofs"][0]["artifact"] = "../secrets.txt"
        self.assertIn("action:schedule:implementation:missing_or_invalid_artifact", self.assess(self.SHA)["blockers"])

    def test_evidence_revision_must_match_tested_source(self):
        self.evidence["proofs"][0]["revision"] = "b"*40
        self.assertIn("action:schedule:implementation:stale_revision", self.assess(self.SHA)["blockers"])

    def test_invalid_manifest_is_error_not_no_go_or_go(self):
        self.manifest["required_personas"] = []
        with self.assertRaises(ValidationError):
            self.assess(self.SHA)

    def test_cli_no_go_uses_exit_2(self):
        manifest_path = self.root / "manifest.json"
        evidence_path = self.root / "proofs.json"
        manifest_path.write_text(json.dumps(self.manifest))
        evidence_path.write_text(json.dumps(self.evidence))
        from contextlib import redirect_stdout
        from io import StringIO
        capture = StringIO()
        with redirect_stdout(capture):
            result = main(["product-acceptance", "--manifest", str(manifest_path), "--evidence", str(evidence_path),
                           "--repo-root", str(self.root), "--source-revision", self.SHA])
        self.assertEqual(2, result)
        self.assertEqual("NO_GO", json.loads(capture.getvalue())["decision"])


if __name__ == "__main__":
    unittest.main()
