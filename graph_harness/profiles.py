from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .model import ValidationError
from .validation import load_json_object, reject_profile_safety_keys, reject_secret_like_keys, reject_secret_like_values


@dataclass(frozen=True)
class DeveloperProfile:
    developer: str | None = None
    preferences: Mapping[str, Any] = field(default_factory=dict)
    source: str | None = None

    @classmethod
    def from_path(cls, path: str | Path) -> "DeveloperProfile":
        candidate = Path(path)
        return cls.from_mapping(load_json_object(candidate, "developer profile"), source=str(candidate))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], *, source: str | None = None) -> "DeveloperProfile":
        unknown = sorted(set(raw) - {"schema_version", "developer", "preferences"})
        if unknown:
            raise ValidationError(f"developer profile: unsupported fields {unknown}")
        if raw.get("schema_version") != "graph-harness.developer-profile.v1":
            raise ValidationError("developer profile schema_version must be graph-harness.developer-profile.v1")
        developer = raw.get("developer")
        if developer is not None and (not isinstance(developer, str) or not developer.strip()):
            raise ValidationError("developer profile developer must be a non-empty string or null")
        preferences = raw.get("preferences", {})
        if not isinstance(preferences, Mapping):
            raise ValidationError("developer profile preferences must be an object")
        reject_secret_like_keys(preferences, label="developer profile")
        reject_secret_like_values(preferences, label="developer profile")
        reject_profile_safety_keys(preferences, label="developer profile")
        return cls(
            developer=developer.strip() if isinstance(developer, str) else None,
            preferences=dict(preferences),
            source=source,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "graph-harness.developer-profile.v1",
            "developer": self.developer,
            "preferences": dict(self.preferences),
            "source": self.source,
        }
