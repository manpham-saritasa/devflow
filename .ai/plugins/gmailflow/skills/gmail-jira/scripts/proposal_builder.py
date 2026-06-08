"""Proposal-building helpers for gmail-jira CLI flow — pure lookups, no generation."""

from __future__ import annotations

from typing import Any


def header_map(headers: list[dict[str, str]]) -> dict[str, str]:
    """Convert Gmail header arrays into case-insensitive lookup map."""
    return {item.get("name", "").lower(): item.get("value", "") for item in headers}


def choose_component(project: dict[str, Any], component_name: str) -> dict[str, str]:
    """Resolve the requested Jira component by exact case-insensitive name."""
    target = component_name.strip().lower()
    for item in project.get("components", []):
        if item.get("name", "").lower() == target:
            return {"id": item["id"], "name": item["name"]}
    return {}


def choose_issue_type(project: dict[str, Any], name: str) -> dict[str, str]:
    """Resolve one Jira issue type by exact name."""
    target = name.strip().lower()
    for item in project.get("issueTypes", []):
        if item.get("name", "").lower() == target:
            return {"id": item["id"], "name": item["name"]}
    return {}
