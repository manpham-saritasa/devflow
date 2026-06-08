"""Repo-local config helpers for gmail-jira caches and name maps."""

from __future__ import annotations

import json
from pathlib import Path


class GmailJiraConfigStore:
    """Load and save gmail-jira local config files under `.local/gmailflow`."""

    def __init__(self, repo_root: Path):
        """Point config access at the shared repo-local GmailFlow folder."""
        self.root = repo_root / ".local" / "gmailflow"
        self.fields_path = self.root / "jira-fields.json"
        self.name_map_path = self.root / "name-map.txt"

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

    def load_name_map(self) -> dict[str, str]:
        """Read optional sender email to friendly first-name mappings."""
        if not self.name_map_path.exists():
            return {}
        items: dict[str, str] = {}
        for raw_line in self.name_map_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            email, name = line.split("=", 1)
            items[email.strip().lower()] = name.strip()
        return items
