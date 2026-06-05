"""Persistence helpers for project-to-Gmail-label mappings."""

from __future__ import annotations

from pathlib import Path


class GmailProjectLabelStore:
    """Load, update, and persist project label mappings for GmailFlow."""

    def __init__(self, repo_root: Path):
        """Point the store at the repo-local project label mapping file."""
        self.path = repo_root / ".local" / "gmailflow" / "project-labels.txt"

    def load(self) -> dict[str, dict[str, str]]:
        """Read saved project label mappings from disk."""
        if not self.path.exists():
            return {}
        items: dict[str, dict[str, str]] = {}
        for raw_line in self.path.read_text(encoding="utf-8").splitlines():
            item = self._parse_line(raw_line)
            if item:
                items[item["project"]] = item
        return items

    def save(self, project_labels: dict[str, dict[str, str]]) -> None:
        """Persist project label mappings using the canonical line format."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            line
            for project in sorted(project_labels)
            if (line := self._format_line(project_labels[project]))
        ]
        content = "\n".join(lines)
        self.path.write_text(content + ("\n" if content else ""), encoding="utf-8")

    def resolve_label_ids(
        self,
        project_labels: dict[str, dict[str, str]],
        gmail_label_map: dict[str, str],
    ) -> tuple[dict[str, dict[str, str]], bool]:
        """Fill in missing Gmail label IDs and save them when discovered."""
        changed = False
        resolved: dict[str, dict[str, str]] = {}
        for project, item in project_labels.items():
            label_name = item.get("label_name", "").strip()
            label_id = item.get("label_id", "").strip()
            actual_label_id = label_id or gmail_label_map.get(label_name, "")
            resolved[project] = {
                "project": project,
                "label_name": label_name,
                "label_id": actual_label_id,
            }
            if actual_label_id and actual_label_id != label_id:
                changed = True
        if changed:
            self.save(resolved)
        return resolved, changed

    def _parse_line(self, raw_line: str) -> dict[str, str] | None:
        """Parse one mapping line into project, label name, and optional label ID."""
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            return None
        parts = [part.strip() for part in line.split("=")]
        if len(parts) < 2:
            return None
        project = parts[0].upper()
        label_name = parts[1]
        label_id = parts[2] if len(parts) >= 3 else ""
        if not project or not label_name:
            return None
        return {"project": project, "label_name": label_name, "label_id": label_id}

    def _format_line(self, item: dict[str, str]) -> str:
        """Format one mapping record for storage in project-labels.txt."""
        project = item.get("project", "").strip().upper()
        label_name = item.get("label_name", "").strip()
        label_id = item.get("label_id", "").strip()
        if not project or not label_name:
            return ""
        return (
            f"{project}={label_name}={label_id}"
            if label_id
            else f"{project}={label_name}"
        )
