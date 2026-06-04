"""Shared helpers for all JiraFlow skills. Import from any skill script."""

import os
import sys
from typing import Any

import yaml


def find_repo_root(start: str) -> str:
    path = os.path.dirname(os.path.abspath(start))
    while path and not os.path.exists(os.path.join(path, ".git")):
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    return path


def load_favorite_projects(root: str) -> list[str]:
    """Read favorite_projects from .local/jiraflow/config.yaml."""
    path = os.path.join(root, ".local", "jiraflow", "config.yaml")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            projects = data.get("favorite_projects") or []
            return [str(p) for p in projects if p]
    except Exception:
        return []
