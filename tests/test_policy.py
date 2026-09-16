from __future__ import annotations

import unittest

from graph_harness.model import ValidationError
from graph_harness.policy import ActionRequest, Decision, PolicyLayer, evaluate_action, resolve_policy
from graph_harness.profiles import DeveloperProfile


class PolicyTests(unittest.TestCase):
    def layer(self, scope: str, *, safety: dict | None = None, preferences: dict | None = None) -> PolicyLayer:
        return PolicyLayer.from_mapping(
            {
                "schema_version": "graph-harness.policy.v1",
                "scope": scope,
                "safety": safety or {},
                "preferences": preferences or {},
            }
        )

    def test_safety_is_monotonic_and_policy_preferences_override_profile(self) -> None:
        workspace = self.layer(
            "workspace",
            safety={"deny_command_patterns": [r"danger"]},
            preferences={"detail": "high", "language": "en"},
        )
        project = self.layer(
            "project",
            safety={"deny_path_patterns": ["*/protected/*"]},
            preferences={"detail": "low"},
        )
        resolved = resolve_policy([workspace, project], profile_preferences={"language": "es", "editor": "vim"})
        self.assertEqual((r"danger",), resolved.safety.deny_command_patterns)
        self.assertEqual(("*/protected/*",), resolved.safety.deny_path_patterns)
        self.assertEqual("low", resolved.preferences["detail"])
        self.assertEqual("en", resolved.preferences["language"])
        self.assertEqual("vim", resolved.preferences["editor"])

    def test_policy_layers_must_be_broad_to_specific(self) -> None:
        with self.assertRaisesRegex(ValidationError, "broad to specific"):
            resolve_policy([self.layer("project"), self.layer("workspace")])

    def test_secret_write_is_absolute_deny_even_with_approval(self) -> None:
        resolved = resolve_policy([])
        result = evaluate_action(
            resolved,
            ActionRequest(content='api_key="sk-abcdefghijklmnopqrstuvwxyz123456"', approved=True),
        )
        self.assertEqual(Decision.DENY, result.decision)

    def test_install_requires_approval(self) -> None:
        resolved = resolve_policy([])
        denied = evaluate_action(resolved, ActionRequest(kind="shell", command="pip install example"))
        allowed = evaluate_action(
            resolved,
            ActionRequest(kind="shell", command="pip install example", approved=True),
        )
        self.assertEqual(Decision.DENY, denied.decision)
        self.assertEqual(Decision.ALLOW, allowed.decision)

    def test_policy_denied_command_cannot_be_approved_away(self) -> None:
        resolved = resolve_policy(
            [self.layer("project", safety={"deny_command_patterns": [r"git\s+push\s+--force"]})]
        )
        result = evaluate_action(
            resolved,
            ActionRequest(kind="shell", command="git push --force origin main", approved=True),
        )
        self.assertEqual(Decision.DENY, result.decision)

    def test_profile_cannot_define_safety_or_credentials(self) -> None:
        with self.assertRaisesRegex(ValidationError, "safety/authority"):
            DeveloperProfile.from_mapping(
                {
                    "schema_version": "graph-harness.developer-profile.v1",
                    "preferences": {"bypass_approval": True},
                }
            )
        with self.assertRaisesRegex(ValidationError, "secret-like"):
            DeveloperProfile.from_mapping(
                {
                    "schema_version": "graph-harness.developer-profile.v1",
                    "preferences": {"github_token": "not-allowed"},
                }
            )
        with self.assertRaisesRegex(ValidationError, "secret-like value"):
            DeveloperProfile.from_mapping(
                {
                    "schema_version": "graph-harness.developer-profile.v1",
                    "preferences": {"note": "sk-abcdefghijklmnopqrstuvwxyz123456"},
                }
            )


if __name__ == "__main__":
    unittest.main()
