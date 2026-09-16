from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .model import ValidationError
from .validation import load_json_object, reject_secret_like_keys, reject_secret_like_values

_SANITIZE_PATTERN = re.compile(r"[^A-Za-z0-9._:/-]+")


def sanitize_attribute_value(value: str) -> str:
    compact = _SANITIZE_PATTERN.sub("-", value.strip()).strip("-")
    return compact[:160]


@dataclass(frozen=True)
class AttributionContext:
    project: str | None = None
    engagement: str | None = None
    workflow_kind: str | None = None
    executor_provider: str | None = None
    executor_model: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
    source: str | None = None

    @classmethod
    def from_path(cls, path: str | Path) -> "AttributionContext":
        candidate = Path(path)
        return cls.from_mapping(load_json_object(candidate, "attribution"), source=str(candidate))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], *, source: str | None = None) -> "AttributionContext":
        unknown = sorted(set(raw) - {"schema_version", "project", "engagement", "workflow", "executor", "metadata"})
        if unknown:
            raise ValidationError(f"attribution: unsupported fields {unknown}")
        if raw.get("schema_version") != "graph-harness.attribution.v1":
            raise ValidationError("attribution.schema_version must be graph-harness.attribution.v1")
        reject_secret_like_keys(raw, label="attribution")
        reject_secret_like_values(raw, label="attribution")
        workflow = raw.get("workflow", {})
        executor = raw.get("executor", {})
        metadata = raw.get("metadata", {})
        for label, value in {"workflow": workflow, "executor": executor, "metadata": metadata}.items():
            if not isinstance(value, Mapping):
                raise ValidationError(f"attribution.{label} must be an object")
        if set(workflow) - {"kind"}:
            raise ValidationError("attribution.workflow supports only the kind field")
        if set(executor) - {"provider", "model"}:
            raise ValidationError("attribution.executor supports only provider and model fields")
        parsed_metadata: dict[str, str] = {}
        for key, value in metadata.items():
            if not isinstance(value, (str, int, float, bool)):
                raise ValidationError(f"attribution.metadata.{key} must be a scalar")
            parsed_metadata[str(key)] = str(value)
        return cls(
            project=_optional_string(raw.get("project"), "project"),
            engagement=_optional_string(raw.get("engagement"), "engagement"),
            workflow_kind=_optional_string(workflow.get("kind"), "workflow.kind"),
            executor_provider=_optional_string(executor.get("provider"), "executor.provider"),
            executor_model=_optional_string(executor.get("model"), "executor.model"),
            metadata=parsed_metadata,
            source=source,
        )

    def as_attributes(self) -> dict[str, str]:
        attributes: dict[str, str] = {}
        candidates = {
            "project": self.project,
            "engagement": self.engagement,
            "workflow.kind": self.workflow_kind,
            "executor.provider": self.executor_provider,
            "executor.model": self.executor_model,
        }
        for key, value in candidates.items():
            if value:
                attributes[key] = sanitize_attribute_value(value)
        for key, value in self.metadata.items():
            clean_key = sanitize_attribute_value(str(key))
            clean_value = sanitize_attribute_value(str(value))
            if clean_key and clean_value:
                attributes[f"meta.{clean_key}"] = clean_value
        return attributes

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "graph-harness.attribution-state.v1",
            "transport_enabled": False,
            "attributes": self.as_attributes(),
            "source": self.source,
        }


def _optional_string(value: Any, label: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(f"attribution.{label} must be a string")
    return value
