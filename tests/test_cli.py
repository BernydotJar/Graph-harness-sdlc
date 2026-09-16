from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from graph_harness.cli import main


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, args: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_existing_runtime_cli_syntax_remains_compatible(self) -> None:
        project = self.root / "project.json"
        events = self.root / "events.jsonl"
        project.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.project.v1",
                    "project_id": "cli-test",
                    "mode": "MVP",
                    "gate_definitions": [
                        {"id": "verification", "required_evidence_kinds": [], "blocking": True}
                    ],
                    "nodes": [
                        {
                            "id": "A",
                            "kind": "feature",
                            "title": "A",
                            "status": "pending",
                            "depends_on": [],
                            "capability": "general",
                            "gates": {},
                            "allowed_paths": [],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        code, stdout, stderr = self.run_cli(
            ["--project", str(project), "--events", str(events), "validate"]
        )
        self.assertEqual(0, code, stderr)
        self.assertTrue(json.loads(stdout)["valid"])

    def test_bootstrap_defaults_to_dry_run(self) -> None:
        code, stdout, stderr = self.run_cli(["bootstrap", "--root", str(self.root)])
        self.assertEqual(0, code, stderr)
        self.assertTrue(json.loads(stdout)["dry_run"])
        self.assertFalse((self.root / ".graph-harness").exists())

    def test_check_action_returns_distinct_deny_exit(self) -> None:
        code, stdout, _stderr = self.run_cli(
            ["check-action", "--command-line", "npm install example"]
        )
        self.assertEqual(3, code)
        self.assertEqual("deny", json.loads(stdout)["decision"])

    def test_provider_render_defaults_to_dry_run(self) -> None:
        shared = self.root / "shared.md"
        shared.write_text("Shared rules\n", encoding="utf-8")
        target_root = self.root / "home"
        target_root.mkdir()
        code, stdout, stderr = self.run_cli(
            [
                "provider-render",
                "--provider",
                "claude",
                "--root",
                str(target_root),
                "--shared-file",
                str(shared),
            ]
        )
        self.assertEqual(0, code, stderr)
        self.assertTrue(json.loads(stdout)["dry_run"])
        self.assertFalse((target_root / ".claude" / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
