from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from .model import ValidationError

_SECRET_KEY_PATTERN = re.compile(
    r"(?:^|[_-])(api[_-]?key|token|secret|password|credential|private[_-]?key|access[_-]?key)(?:$|[_-])",
    re.IGNORECASE,
)

_SECRET_VALUE_PATTERNS = (
    re.compile(r"(?im)-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{20,}\b"),
)

_SAFETY_PROFILE_KEY_PATTERN = re.compile(
    r"(?:safety|approval|permission|bypass|credential|secret|token|password|deny[_-]?rule|allow[_-]?destructive)",
    re.IGNORECASE,
)


def load_json_object(path: str | Path, label: str) -> dict[str, Any]:
    candidate = Path(path)
    try:
        raw = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"{label}: cannot read valid JSON from {candidate}: {error}") from error
    if not isinstance(raw, dict):
        raise ValidationError(f"{label}: root must be a JSON object")
    return raw


def reject_secret_like_keys(value: Any, *, label: str = "document", path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            location = ".".join((*path, key))
            if _SECRET_KEY_PATTERN.search(key):
                raise ValidationError(f"{label}: secret-like key is not allowed: {location}")
            reject_secret_like_keys(child, label=label, path=(*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_secret_like_keys(child, label=label, path=(*path, str(index)))


def reject_secret_like_values(value: Any, *, label: str = "document", path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            reject_secret_like_values(child, label=label, path=(*path, str(raw_key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_secret_like_values(child, label=label, path=(*path, str(index)))
    elif isinstance(value, str):
        for pattern in _SECRET_VALUE_PATTERNS:
            if pattern.search(value):
                location = ".".join(path) or "<root>"
                raise ValidationError(f"{label}: secret-like value is not allowed at {location}")


def reject_profile_safety_keys(value: Any, *, label: str = "developer profile", path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            location = ".".join((*path, key))
            if _SAFETY_PROFILE_KEY_PATTERN.search(key):
                raise ValidationError(f"{label}: safety/authority key is not allowed in preferences: {location}")
            reject_profile_safety_keys(child, label=label, path=(*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_profile_safety_keys(child, label=label, path=(*path, str(index)))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str | Path) -> str:
    candidate = Path(path)
    digest = hashlib.sha256()
    try:
        with candidate.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise ValidationError(f"cannot hash {candidate}: {error}") from error
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def ensure_string_mapping(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{label} must be an object")
    return {str(key): child for key, child in value.items()}
