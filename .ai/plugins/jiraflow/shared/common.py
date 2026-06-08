"""Shared JiraFlow config helpers."""

from __future__ import annotations

import json
from pathlib import Path


class JiraCreateConfigStore:
    """Load and save Jira create caches under `.local/gmailflow`."""

    def __init__(self, repo_root: Path):
        """Point config access at shared repo-local GmailFlow folder."""
        self.root = repo_root / ".local" / "gmailflow"
        self.fields_path = self.root / "jira-fields.json"

    def load_jira_fields(self) -> dict[str, dict[str, str | None]]:
        """Read cached Jira custom field ids for each project."""
        if not self.fields_path.exists():
            return {}
        return json.loads(self.fields_path.read_text(encoding="utf-8"))

    def save_jira_fields(self, data: dict[str, dict[str, str | None]]) -> None:
        """Persist Jira custom field ids in stable JSON format."""
        self.root.mkdir(parents=True, exist_ok=True)
        content = json.dumps(data, indent=2, sort_keys=True) + "\n"
        self.fields_path.write_text(content, encoding="utf-8")


def load_env(env_path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE env files without exporting process env."""
    data: dict[str, str] = {}
    if not env_path.exists():
        return data
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data
