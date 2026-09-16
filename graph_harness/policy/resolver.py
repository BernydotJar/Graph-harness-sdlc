from __future__ import annotations

from collections.abc import Iterable

from ..model import ValidationError
from .model import PolicyLayer, ResolvedPolicy, SafetyPolicy

_SCOPE_ORDER = {
    "organization": 0,
    "workspace": 1,
    "customer": 2,
    "solution": 3,
    "project": 4,
    "repository": 5,
}


def _ordered_union(groups: Iterable[tuple[str, ...]]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for item in group:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return tuple(result)


def resolve_policy(layers: Iterable[PolicyLayer], *, profile_preferences: dict | None = None) -> ResolvedPolicy:
    ordered = tuple(layers)
    positions = [_SCOPE_ORDER[layer.scope] for layer in ordered]
    if positions != sorted(positions):
        raise ValidationError(
            "policy layers must be supplied broad to specific: organization, workspace, customer, solution, project, repository"
        )
    safety = SafetyPolicy(
        deny_command_patterns=_ordered_union(layer.safety.deny_command_patterns for layer in ordered),
        warn_command_patterns=_ordered_union(layer.safety.warn_command_patterns for layer in ordered),
        deny_path_patterns=_ordered_union(layer.safety.deny_path_patterns for layer in ordered),
        approval_required_patterns=_ordered_union(layer.safety.approval_required_patterns for layer in ordered),
        secret_patterns=_ordered_union(layer.safety.secret_patterns for layer in ordered),
    )
    # Developer preferences are intentionally the weakest behavioral layer. Project and
    # repository policy may override them; they can never alter the safety collections above.
    preferences: dict = dict(profile_preferences or {})
    for layer in ordered:
        preferences.update(layer.preferences)
    return ResolvedPolicy(
        safety=safety,
        preferences=preferences,
        scopes=tuple(layer.scope for layer in ordered),
        sources=tuple(layer.source or f"<{layer.scope}>" for layer in ordered),
    )
