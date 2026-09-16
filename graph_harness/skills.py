from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .model import ValidationError
from .validation import load_json_object

_ALLOWED_STATUSES = {"stable", "experimental"}


@dataclass(frozen=True)
class SkillEntry:
    id: str
    path: str
    status: str
    description: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "path": self.path,
            "status": self.status,
            "description": self.description,
        }


@dataclass(frozen=True)
class SkillRegistry:
    entries: tuple[SkillEntry, ...]
    source: str

    @classmethod
    def from_path(cls, path: str | Path) -> "SkillRegistry":
        candidate = Path(path)
        raw = load_json_object(candidate, "skill registry")
        if raw.get("schema_version") != "graph-harness.skills.v1":
            raise ValidationError("skill registry schema_version must be graph-harness.skills.v1")
        unknown = sorted(set(raw) - {"schema_version", "skills"})
        if unknown:
            raise ValidationError(f"skill registry: unsupported fields {unknown}")
        skills = raw.get("skills")
        if not isinstance(skills, list):
            raise ValidationError("skill registry skills must be an array")
        entries: list[SkillEntry] = []
        seen_ids: set[str] = set()
        for index, item in enumerate(skills):
            if not isinstance(item, Mapping):
                raise ValidationError(f"skill registry skills[{index}] must be an object")
            unknown_entry = sorted(set(item) - {"id", "path", "status", "description"})
            if unknown_entry:
                raise ValidationError(f"skill registry skills[{index}]: unsupported fields {unknown_entry}")
            skill_id = _required_string(item, "id", index)
            skill_path = _required_string(item, "path", index)
            status = _required_string(item, "status", index)
            description = _required_string(item, "description", index)
            if skill_id in seen_ids:
                raise ValidationError(f"skill registry contains duplicate id {skill_id!r}")
            seen_ids.add(skill_id)
            if status not in _ALLOWED_STATUSES:
                raise ValidationError(
                    f"skill registry skill {skill_id!r} status must be one of {sorted(_ALLOWED_STATUSES)}"
                )
            relative = Path(skill_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValidationError(f"skill registry skill {skill_id!r} path must stay within the skills directory")
            absolute = candidate.parent / relative
            if not absolute.is_file():
                raise ValidationError(f"skill registry skill {skill_id!r} points to missing file {skill_path!r}")
            entries.append(SkillEntry(skill_id, skill_path, status, description))
        return cls(entries=tuple(entries), source=str(candidate))

    def by_status(self, status: str | None = None) -> tuple[SkillEntry, ...]:
        if status is None:
            return self.entries
        if status not in _ALLOWED_STATUSES:
            raise ValidationError(f"skill status must be one of {sorted(_ALLOWED_STATUSES)}")
        return tuple(entry for entry in self.entries if entry.status == status)

    def as_dict(self, *, status: str | None = None) -> dict[str, Any]:
        selected = self.by_status(status)
        return {
            "schema_version": "graph-harness.skills-state.v1",
            "source": self.source,
            "count": len(selected),
            "skills": [entry.as_dict() for entry in selected],
        }


def _required_string(item: Mapping[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"skill registry skills[{index}].{key} must be a non-empty string")
    return value.strip()
