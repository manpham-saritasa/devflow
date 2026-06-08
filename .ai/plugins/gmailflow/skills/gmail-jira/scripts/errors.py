"""Small error helpers for gmail-jira CLI flow."""

from __future__ import annotations

from typing import Any


def build_error(message: str, missing: list[str] | None = None) -> dict[str, Any]:
    """Build one structured error payload for CLI output."""
    return {"ok": False, "message": message, "missing": missing or []}


def require_choice(item: dict[str, str], label: str) -> dict[str, str]:
    """Require one resolved Jira selection before continuing."""
    if item:
        return item
    raise ValueError(f"Unable to resolve Jira {label}.")
