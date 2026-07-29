from __future__ import annotations

import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

from .model import EventType, ValidationError

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class StoredEvent:
    schema_version: str
    event_id: str
    sequence: int
    occurred_at: str
    project_id: str
    event_type: EventType
    node_id: str | None
    node_revision: int | None
    actor: str
    payload: Mapping[str, Any]
    previous_event_hash: str
    event_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "sequence": self.sequence,
            "occurred_at": self.occurred_at,
            "project_id": self.project_id,
            "event_type": self.event_type.value,
            "node_id": self.node_id,
            "node_revision": self.node_revision,
            "actor": self.actor,
            "payload": dict(self.payload),
            "previous_event_hash": self.previous_event_hash,
            "event_hash": self.event_hash,
        }


class EventStore:
    """Append-only JSONL store with a verified SHA-256 hash chain."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> list[StoredEvent]:
        if not self.path.exists():
            return []
        events: list[StoredEvent] = []
        previous_hash = GENESIS_HASH
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            raise ValidationError(f"{self.path}: cannot read event store: {error}") from error
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValidationError(f"{self.path}:{line_number}: invalid JSON: {error}") from error
            event = self._parse(raw, line_number)
            expected_sequence = len(events) + 1
            if event.sequence != expected_sequence:
                raise ValidationError(
                    f"{self.path}:{line_number}: expected sequence {expected_sequence}, got {event.sequence}"
                )
            if event.previous_event_hash != previous_hash:
                raise ValidationError(
                    f"{self.path}:{line_number}: previous_event_hash does not match chain"
                )
            expected_hash = self._event_hash(event.as_dict())
            if event.event_hash != expected_hash:
                raise ValidationError(f"{self.path}:{line_number}: event_hash mismatch")
            previous_hash = event.event_hash
            events.append(event)
        return events

    def append(
        self,
        *,
        project_id: str,
        event_type: EventType,
        actor: str,
        payload: Mapping[str, Any],
        node_id: str | None = None,
        node_revision: int | None = None,
        expected_last_event_id: str | None = None,
    ) -> StoredEvent:
        if not actor.strip():
            raise ValidationError("event actor must be non-empty")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_RDWR | os.O_CREAT
        descriptor = os.open(self.path, flags, 0o644)
        try:
            with os.fdopen(descriptor, "r+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                handle.seek(0)
                raw_text = handle.read()
                existing = self._load_text(raw_text)
                last = existing[-1] if existing else None
                if expected_last_event_id is not None:
                    actual = last.event_id if last else None
                    if actual != expected_last_event_id:
                        raise ValidationError(
                            "event store changed concurrently: "
                            f"expected last event {expected_last_event_id!r}, got {actual!r}"
                        )
                raw: dict[str, Any] = {
                    "schema_version": "graph-harness.event.v1",
                    "event_id": str(uuid4()),
                    "sequence": len(existing) + 1,
                    "occurred_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "project_id": project_id,
                    "event_type": event_type.value,
                    "node_id": node_id,
                    "node_revision": node_revision,
                    "actor": actor.strip(),
                    "payload": dict(payload),
                    "previous_event_hash": last.event_hash if last else GENESIS_HASH,
                    "event_hash": "",
                }
                raw["event_hash"] = self._event_hash(raw)
                event = self._parse(raw, len(existing) + 1)
                handle.seek(0, os.SEEK_END)
                if handle.tell() and not raw_text.endswith("\n"):
                    handle.write("\n")
                handle.write(json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
                return event
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise

    def _load_text(self, text: str) -> list[StoredEvent]:
        if not text:
            return []
        temporary = self.path
        events: list[StoredEvent] = []
        previous_hash = GENESIS_HASH
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValidationError(f"{temporary}:{line_number}: invalid JSON: {error}") from error
            event = self._parse(raw, line_number)
            if event.sequence != len(events) + 1:
                raise ValidationError(f"{temporary}:{line_number}: non-contiguous sequence")
            if event.previous_event_hash != previous_hash:
                raise ValidationError(f"{temporary}:{line_number}: broken hash chain")
            if event.event_hash != self._event_hash(event.as_dict()):
                raise ValidationError(f"{temporary}:{line_number}: event_hash mismatch")
            previous_hash = event.event_hash
            events.append(event)
        return events

    @staticmethod
    def _event_hash(raw: Mapping[str, Any]) -> str:
        material = dict(raw)
        material["event_hash"] = ""
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _parse(raw: Any, line_number: int) -> StoredEvent:
        if not isinstance(raw, Mapping):
            raise ValidationError(f"event line {line_number}: root must be an object")
        required_strings = (
            "schema_version",
            "event_id",
            "occurred_at",
            "project_id",
            "event_type",
            "actor",
            "previous_event_hash",
            "event_hash",
        )
        for key in required_strings:
            if not isinstance(raw.get(key), str) or not raw[key]:
                raise ValidationError(f"event line {line_number}: {key} must be non-empty")
        if raw["schema_version"] != "graph-harness.event.v1":
            raise ValidationError(f"event line {line_number}: unsupported schema_version")
        if not isinstance(raw.get("sequence"), int) or raw["sequence"] < 1:
            raise ValidationError(f"event line {line_number}: sequence must be a positive integer")
        if raw.get("node_id") is not None and not isinstance(raw.get("node_id"), str):
            raise ValidationError(f"event line {line_number}: node_id must be a string or null")
        if raw.get("node_revision") is not None and (
            not isinstance(raw.get("node_revision"), int) or raw["node_revision"] < 0
        ):
            raise ValidationError(
                f"event line {line_number}: node_revision must be a non-negative integer or null"
            )
        if not isinstance(raw.get("payload"), Mapping):
            raise ValidationError(f"event line {line_number}: payload must be an object")
        try:
            event_type = EventType(raw["event_type"])
        except ValueError as error:
            raise ValidationError(f"event line {line_number}: unknown event_type") from error
        for hash_key in ("previous_event_hash", "event_hash"):
            value = raw[hash_key]
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValidationError(f"event line {line_number}: {hash_key} must be lowercase SHA-256")
        return StoredEvent(
            schema_version=raw["schema_version"],
            event_id=raw["event_id"],
            sequence=raw["sequence"],
            occurred_at=raw["occurred_at"],
            project_id=raw["project_id"],
            event_type=event_type,
            node_id=raw.get("node_id"),
            node_revision=raw.get("node_revision"),
            actor=raw["actor"],
            payload=dict(raw["payload"]),
            previous_event_hash=raw["previous_event_hash"],
            event_hash=raw["event_hash"],
        )


def event_ids(events: Iterable[StoredEvent]) -> set[str]:
    return {event.event_id for event in events}
