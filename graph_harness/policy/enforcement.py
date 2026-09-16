from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from .model import ResolvedPolicy


class Decision(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    DENY = "deny"


@dataclass(frozen=True)
class ActionRequest:
    kind: str = "generic"
    command: str = ""
    paths: tuple[str, ...] = ()
    content: str = ""
    approved: bool = False


@dataclass(frozen=True)
class ActionEvaluation:
    decision: Decision
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"decision": self.decision.value, "reasons": list(self.reasons)}


_BUILTIN_INSTALL_PATTERNS = (
    r"(?i)(^|[\s;&|])npx(?:\.cmd)?(?:[\s;&|]|$)",
    r"(?i)(^|[\s;&|])npm(?:\.cmd)?\s+(?:install|i|add|exec)\b",
    r"(?i)(^|[\s;&|])pnpm(?:\.cmd)?\s+(?:install|add|dlx|exec)\b",
    r"(?i)(^|[\s;&|])yarn(?:\.cmd)?\s+(?:add|install|dlx)\b",
    r"(?i)(^|[\s;&|])(?:python|python3|py)(?:\.exe)?\s+-m\s+pip\s+install\b",
    r"(?i)(^|[\s;&|])pip3?(?:\.exe)?\s+install\b",
    r"(?i)(^|[\s;&|])uv(?:\.exe)?\s+(?:tool\s+install|pip\s+install)\b",
    r"(?i)(^|[\s;&|])winget(?:\.exe)?\s+install\b",
)

_BUILTIN_DESTRUCTIVE_PATTERNS = (
    r"(?i)(^|[\s;&|])(?:rm\s+-rf|git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|drop\s+database|truncate\s+table)\b",
    r"(?i)(^|[\s;&|])(?:Remove-Item|del|erase|rmdir)(?:\s|$)",
)

_BUILTIN_SECRET_PATTERNS = (
    r"(?im)-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----",
    r"(?i)\bAKIA[0-9A-Z]{16}\b",
    r"(?i)\bsk-[A-Za-z0-9_-]{20,}\b",
    r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]",
)


def _matches_any(text: str, patterns: Iterable[str]) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text):
            return pattern
    return None


def _normalize_path(path: str) -> str:
    try:
        return str(Path(path).expanduser().resolve(strict=False))
    except (OSError, RuntimeError):
        return path


def _path_matches(path: str, pattern: str) -> bool:
    normalized = _normalize_path(path)
    normalized_pattern = str(Path(pattern).expanduser()) if not any(char in pattern for char in "*?[") else pattern
    return fnmatch.fnmatch(normalized, normalized_pattern) or fnmatch.fnmatch(path, pattern)


def evaluate_action(policy: ResolvedPolicy, request: ActionRequest) -> ActionEvaluation:
    deny_reasons: list[str] = []
    approval_reasons: list[str] = []
    warn_reasons: list[str] = []

    if request.content:
        pattern = _matches_any(request.content, (*_BUILTIN_SECRET_PATTERNS, *policy.safety.secret_patterns))
        if pattern:
            deny_reasons.append("content matches a secret-like write pattern")

    if request.command:
        denied = _matches_any(request.command, policy.safety.deny_command_patterns)
        if denied:
            deny_reasons.append(f"command matches denied policy pattern: {denied}")
        install = _matches_any(request.command, _BUILTIN_INSTALL_PATTERNS)
        if install:
            approval_reasons.append("internet/package installation requires explicit approval")
        destructive = _matches_any(request.command, _BUILTIN_DESTRUCTIVE_PATTERNS)
        if destructive:
            approval_reasons.append("destructive command requires explicit approval")
        approval_pattern = _matches_any(request.command, policy.safety.approval_required_patterns)
        if approval_pattern:
            approval_reasons.append(f"command matches approval-required policy pattern: {approval_pattern}")
        warning = _matches_any(request.command, policy.safety.warn_command_patterns)
        if warning:
            warn_reasons.append(f"command matches warning policy pattern: {warning}")

    for path in request.paths:
        for pattern in policy.safety.deny_path_patterns:
            if _path_matches(path, pattern):
                deny_reasons.append(f"path {path!r} matches denied path policy: {pattern}")

    if deny_reasons:
        return ActionEvaluation(Decision.DENY, tuple(dict.fromkeys(deny_reasons)))
    if approval_reasons and not request.approved:
        return ActionEvaluation(Decision.DENY, tuple(dict.fromkeys(approval_reasons)))
    if warn_reasons:
        return ActionEvaluation(Decision.WARN, tuple(dict.fromkeys(warn_reasons)))
    if approval_reasons and request.approved:
        return ActionEvaluation(Decision.ALLOW, ("explicit approval satisfied approval-gated rules",))
    return ActionEvaluation(Decision.ALLOW, ())
