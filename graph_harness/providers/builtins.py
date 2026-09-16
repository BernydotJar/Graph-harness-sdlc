from __future__ import annotations

from pathlib import Path

from ..model import ValidationError
from .base import ProviderAdapter


class ClaudeAdapter(ProviderAdapter):
    provider_id = "claude"
    relative_target = Path(".claude/CLAUDE.md")


class CodexAdapter(ProviderAdapter):
    provider_id = "codex"
    relative_target = Path(".codex/AGENTS.md")


class GeminiAdapter(ProviderAdapter):
    provider_id = "gemini"
    relative_target = Path(".gemini/GEMINI.md")


_ADAPTERS = {
    "claude": ClaudeAdapter,
    "codex": CodexAdapter,
    "gemini": GeminiAdapter,
}


def get_provider_adapter(provider: str) -> ProviderAdapter:
    normalized = provider.strip().lower()
    try:
        return _ADAPTERS[normalized]()
    except KeyError as error:
        raise ValidationError(
            f"unknown provider {provider!r}; supported built-in coding-agent providers: {sorted(_ADAPTERS)}"
        ) from error


def provider_ids() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))
