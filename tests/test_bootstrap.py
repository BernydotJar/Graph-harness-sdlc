from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from graph_harness.bootstrap import apply_bootstrap, run_preflight
from graph_harness.model import ValidationError


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_bootstrap_dry_run_is_side_effect_free(self) -> None:
        plan = apply_bootstrap(self.root, dry_run=True)
        self.assertTrue(plan.actions)
        self.assertFalse((self.root / ".graph-harness").exists())
        self.assertTrue(all(action.action == "create" for action in plan.actions))

    def test_bootstrap_apply_never_overwrites_existing_file(self) -> None:
        control = self.root / ".graph-harness"
        control.mkdir()
        policy = control / "policy.json"
        policy.write_text("KEEP-ME", encoding="utf-8")
        plan = apply_bootstrap(self.root, dry_run=False)
        self.assertEqual("KEEP-ME", policy.read_text(encoding="utf-8"))
        actions = {action.path: action.action for action in plan.actions}
        self.assertEqual("skip-existing", actions[".graph-harness/policy.json"])
        self.assertTrue((control / "developer.json").is_file())

    def test_preflight_detects_identity_and_required_commands(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("test\n", encoding="utf-8")
        (self.root / "pyproject.toml").write_text("[project]\nname = 'example'\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=self.root, check=True)
        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=self.root, text=True, stdout=subprocess.PIPE, check=True
        ).stdout.strip()
        expectation = self.root / "expect.json"
        expectation.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.preflight.v1",
                    "identity": {"work_root": str(self.root), "branch": branch},
                    "environment": {"python": ">=3.11", "require_commands": ["git"], "frameworks": ["python"]},
                }
            ),
            encoding="utf-8",
        )
        result = run_preflight(self.root, expectations_path=expectation)
        self.assertTrue(result.ok)
        self.assertTrue(result.observed["commands"]["git"]["available"])
        self.assertIn("python", result.observed["frameworks"])

    def test_preflight_fails_closed_on_identity_mismatch(self) -> None:
        expectation = self.root / "expect.json"
        expectation.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.preflight.v1",
                    "identity": {"work_root": str(self.root / "wrong")},
                    "environment": {"require_commands": []},
                }
            ),
            encoding="utf-8",
        )
        result = run_preflight(self.root, expectations_path=expectation)
        self.assertFalse(result.ok)
        self.assertTrue(any(f.code == "identity-work_root-mismatch" for f in result.findings))

    def test_preflight_rejects_secret_like_expectation_keys(self) -> None:
        expectation = self.root / "expect.json"
        expectation.write_text(
            json.dumps(
                {
                    "schema_version": "graph-harness.preflight.v1",
                    "identity": {},
                    "environment": {"api_key": "should-not-be-here"},
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValidationError, "secret-like"):
            run_preflight(self.root, expectations_path=expectation)


if __name__ == "__main__":
    unittest.main()
