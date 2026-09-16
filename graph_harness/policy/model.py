from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ..model import ValidationError
from ..validation import load_json_object

_ALLOWED_SCOPES = {
    "organization",
    "workspace",
    "customer",
    "solution",
    "project",
    "repository",
}

_SAFETY_FIELDS = (
    "deny_command_patterns",
    "warn_command_patterns",
    "deny_path_patterns",
    "approval_required_patterns",
    "secret_patterns",
)


@dataclass(frozen=True)
class SafetyPolicy:
    deny_command_patterns: tuple[str, ...] = ()
    warn_command_patterns: tuple[str, ...] = ()
    deny_path_patterns: tuple[str, ...] = ()
    approval_required_patterns: tuple[str, ...] = ()
    secret_patterns: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, list[str]]:
        return {field_name: list(getattr(self, field_name)) for field_name in _SAFETY_FIELDS}


@dataclass(frozen=True)
class PolicyLayer:
    scope: str
    safety: SafetyPolicy = field(default_factory=SafetyPolicy)
    preferences: Mapping[str, Any] = field(default_factory=dict)
    source: str | None = None

    @classmethod
    def from_path(cls, path: str | Path) -> "PolicyLayer":
        candidate = Path(path)
        return cls.from_mapping(load_json_object(candidate, "policy"), source=str(candidate))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], *, source: str | None = None) -> "PolicyLayer":
        unknown = sorted(set(raw) - {"schema_version", "scope", "safety", "preferences"})
        if unknown:
            raise ValidationError(f"policy: unsupported fields {unknown}")
        if raw.get("schema_version") != "graph-harness.policy.v1":
            raise ValidationError("policy.schema_version must be graph-harness.policy.v1")
        scope = raw.get("scope")
        if not isinstance(scope, str) or scope not in _ALLOWED_SCOPES:
            raise ValidationError(f"policy.scope must be one of {sorted(_ALLOWED_SCOPES)}")
        safety_raw = raw.get("safety", {})
        if not isinstance(safety_raw, Mapping):
            raise ValidationError("policy.safety must be an object")
        unknown_safety = sorted(set(safety_raw) - set(_SAFETY_FIELDS))
        if unknown_safety:
            raise ValidationError(f"policy.safety: unsupported fields {unknown_safety}")
        parsed: dict[str, tuple[str, ...]] = {}
        for field_name in _SAFETY_FIELDS:
            values = safety_raw.get(field_name, [])
            if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
                raise ValidationError(f"policy.safety.{field_name} must be an array of non-empty strings")
            for pattern in values:
                if field_name != "deny_path_patterns":
                    try:
                        re.compile(pattern)
                    except re.error as error:
                        raise ValidationError(
                            f"policy.safety.{field_name} contains invalid regex {pattern!r}: {error}"
                        ) from error
            parsed[field_name] = tuple(values)
        preferences = raw.get("preferences", {})
        if not isinstance(preferences, Mapping):
            raise ValidationError("policy.preferences must be an object")
        return cls(
            scope=scope,
            safety=SafetyPolicy(**parsed),
            preferences=dict(preferences),
            source=source,
        )


@dataclass(frozen=True)
class ResolvedPolicy:
    safety: SafetyPolicy
    preferences: Mapping[str, Any]
    scopes: tuple[str, ...]
    sources: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "graph-harness.resolved-policy.v1",
            "scopes": list(self.scopes),
            "sources": list(self.sources),
            "safety": self.safety.as_dict(),
            "preferences": dict(self.preferences),
        }
