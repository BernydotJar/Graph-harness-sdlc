from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from graph_harness.doctor import run_doctor
from graph_harness.model import ValidationError
from graph_harness.providers import get_provider_adapter
from graph_harness.skills import SkillRegistry
from graph_harness.telemetry import AttributionContext


class ControlPlaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_provider_plan_is_dry_and_apply_backs_up_and_records_manifest(self) -> None:
        adapter = get_provider_adapter("codex")
        target = self.root / ".codex" / "AGENTS.md"
        plan = adapter.plan(target_root=self.root, shared_text="shared")
        self.assertEqual("create", plan.action)
        self.assertFalse(target.exists())

        adapter.apply(
            target_root=self.root,
            shared_text="shared",
            manifest_root=self.root,
            sources={},
        )
        self.assertTrue(target.is_file())
        original = target.read_text(encoding="utf-8")
        second = adapter.apply(
            target_root=self.root,
            shared_text="changed",
            manifest_root=self.root,
            sources={},
        )
        self.assertEqual("replace-with-backup", second.action)
        self.assertIsNotNone(second.backup)
        self.assertEqual(original, Path(second.backup).read_text(encoding="utf-8"))
        manifest = json.loads((self.root / ".graph-harness" / "provider-manifest.json").read_text())
        self.assertIn("codex", manifest["projections"])

    def test_invalid_provider_manifest_fails_before_target_mutation(self) -> None:
        adapter = get_provider_adapter("gemini")
        target = self.root / ".gemini" / "GEMINI.md"
        target.parent.mkdir(parents=True)
        target.write_text("original\n", encoding="utf-8")
        control = self.root / ".graph-harness"
        control.mkdir()
        (control / "provider-manifest.json").write_text("{not-json", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "provider manifest is invalid"):
            adapter.apply(
                target_root=self.root,
                shared_text="replacement",
                manifest_root=self.root,
                sources={},
            )
        self.assertEqual("original\n", target.read_text(encoding="utf-8"))

    def test_doctor_detects_provider_target_drift_without_repair(self) -> None:
        adapter = get_provider_adapter("claude")
        adapter.apply(
            target_root=self.root,
            shared_text="shared",
            manifest_root=self.root,
            sources={},
        )
        target = self.root / ".claude" / "CLAUDE.md"
        target.write_text("manual drift\n", encoding="utf-8")
        before = target.read_text(encoding="utf-8")
        report = run_doctor(self.root)
        self.assertTrue(any(item.code == "provider-target-drift" for item in report.findings))
        self.assertEqual(before, target.read_text(encoding="utf-8"))

    def test_skill_registry_supports_lifecycle_and_validates_missing_files(self) -> None:
        skills = self.root / "skills"
        (skills / "one").mkdir(parents=True)
        (skills / "one" / "skill.md").write_text("# One\n", encoding="utf-8")
        registry = skills / "registry.json"
        registry.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.skills.v1",
                    "skills": [
                        {"id": "one", "path": "one/skill.md", "status": "experimental", "description": "One"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        loaded = SkillRegistry.from_path(registry)
        self.assertEqual(1, len(loaded.by_status("experimental")))
        registry.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.skills.v1",
                    "skills": [
                        {"id": "missing", "path": "missing/skill.md", "status": "stable", "description": "Missing"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValidationError, "missing file"):
            SkillRegistry.from_path(registry)

    def test_attribution_is_local_sanitized_and_secret_keys_are_rejected(self) -> None:
        context = AttributionContext.from_mapping(
            {
                "schema_version": "graph-harness.attribution.v1",
                "project": "My Project",
                "engagement": "ACME 123",
                "workflow": {"kind": "AI + deterministic workflow"},
                "executor": {"provider": "example", "model": "model 1"},
                "metadata": {"team": "Applied AI"},
            }
        )
        rendered = context.as_dict()
        self.assertFalse(rendered["transport_enabled"])
        self.assertEqual("My-Project", rendered["attributes"]["project"])
        self.assertEqual("AI-deterministic-workflow", rendered["attributes"]["workflow.kind"])
        with self.assertRaisesRegex(ValidationError, "secret-like"):
            AttributionContext.from_mapping(
                {
                    "schema_version": "graph-harness.attribution.v1",
                    "project": "x",
                    "metadata": {"access_token": "nope"},
                }
            )

    def test_uipath_is_not_a_builtin_coding_provider(self) -> None:
        with self.assertRaisesRegex(ValidationError, "unknown provider"):
            get_provider_adapter("uipath")


if __name__ == "__main__":
    unittest.main()
