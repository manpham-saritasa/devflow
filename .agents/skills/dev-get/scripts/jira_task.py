from dataclasses import dataclass, field
from typing import Any

from attachment_info import AttachmentInfo
from comment import Comment
from subtask_info import SubtaskInfo


@dataclass
class JiraTask:
    key: str
    summary: str
    status: str
    priority: str
    issuetype: str
    assignee: str
    reporter: str
    labels: list[str]
    components: list[str]
    fix_versions: list[str]
    created: str
    updated: str
    due_date: str
    resolution: str
    resolution_date: str
    description_raw: dict[str, Any] | None
    description_text: str
    id: str = ""
    description_html: str = ""
    estimated: str = "None"
    spent: str = "None"
    estimated_seconds: int | None = None
    spent_seconds: int | None = None
    epic_key: str | None = None
    epic_summary: str | None = None
    sprint: str | None = None
    story_points: str | None = None
    parent_key: str | None = None
    parent_summary: str = ""
    parent_type: str | None = None
    tags: list[str] = field(default_factory=list)
    subtask_keys: list[str] = field(default_factory=list)
    subtasks_detail: list[SubtaskInfo] = field(default_factory=list)
    linked_issues: list[dict[str, str]] = field(default_factory=list)
    attachments: list[AttachmentInfo] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)

    @property
    def url(self) -> str:
        return ""

    @staticmethod
    def browse_url(jira_url: str, key: str) -> str:
        return f"{jira_url}/browse/{key}"

    @property
    def component_str(self) -> str:
        return ", ".join(self.components) if self.components else "None"

    @property
    def label_str(self) -> str:
        return ", ".join(self.labels) if self.labels else "None"

    @property
    def fix_version_str(self) -> str:
        return ", ".join(self.fix_versions) if self.fix_versions else "None"

    def epic_md(self, jira_url: str = "") -> str:
        if not self.epic_key:
            return "None"
        link = f"[{self.epic_key}]({self.browse_url(jira_url, self.epic_key)})"
        summary = self.epic_summary or ""
        return f"{link} \u2014 {summary}" if summary else link

    def sprint_md(self) -> str:
        return self.sprint or "None"

    def parent_md(self, jira_url: str = "") -> str:
        if not self.parent_key:
            return "None"
        link = f"[{self.parent_key}]({self.browse_url(jira_url, self.parent_key)})"
        ptype = f" ({self.parent_type})" if self.parent_type else ""
        return f"{link} \u2014 {self.parent_summary}{ptype}"

    def subtasks_md(self, jira_url: str = "") -> str:
        if not self.subtasks_detail:
            return " None"
        items = sorted(self.subtasks_detail, key=lambda s: s.summary.lower())
        lines = []
        for st in items:
            lines.append(
                f"  - [{st.key}]({self.browse_url(jira_url, st.key)}):"
                f" {st.summary} [{st.status}]"
            )
        return "\n" + "\n".join(lines)

    def related_tasks_md(self, jira_url: str = "") -> str:
        if not self.linked_issues:
            return "_(none)_"
        lines = []
        for li in self.linked_issues:
            lines.append(
                f"- **{li['type']}** [{li['key']}]({self.browse_url(jira_url, li['key'])}):"
                f" {li['summary']} [{li.get('status', '?')}]"
            )
        return "\n".join(lines)

    def attachments_md(self) -> str:
        if not self.attachments:
            return "_(none)_"
        lines = []
        for a in self.attachments:
            size_txt = f" ({a.size} bytes)" if a.size is not None else ""
            if a.url:
                lines.append(f"- [{a.filename}]({a.url}){size_txt}")
            else:
                lines.append(f"- {a.filename}{size_txt}")
        return "\n".join(lines)

    def tags_md(self, jira_url: str = "", tags_field_id: str = "") -> str:
        if not self.tags:
            return "None"
        if not tags_field_id:
            return ", ".join(self.tags)
        field_num = tags_field_id.replace("customfield_", "")
        parts = []
        for v in self.tags:
            encoded = v.replace(" ", "%20")
            url = f"{jira_url}/issues/?jql=cf%5B{field_num}%5D%20%3D%20%22{encoded}%22"
            parts.append(f"[{v}]({url})")
        return ", ".join(parts)

    def estimated_str(self) -> str:
        from jira_utils import JiraUtils

        return JiraUtils.format_seconds(self.estimated_seconds)

    def spent_str(self) -> str:
        from jira_utils import JiraUtils

        return JiraUtils.format_seconds(self.spent_seconds)

    def to_json_record(
        self, download_path_rel: str, jira_url: str = ""
    ) -> dict[str, Any]:
        return {
            "task_key": self.key,
            "task_summary": self.summary,
            "status": self.status,
            "issue_type": self.issuetype,
            "priority": self.priority,
            "estimated": self.estimated_str(),
            "spent": self.spent_str(),
            "estimated_seconds": self.estimated_seconds,
            "spent_seconds": self.spent_seconds,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "components": self.components,
            "labels": self.labels,
            "fix_versions": self.fix_versions,
            "created": self.created or None,
            "updated": self.updated or None,
            "due_date": self.due_date if self.due_date != "None" else None,
            "resolution": self.resolution
            if self.resolution != "Unresolved"
            else "None",
            "resolution_date": self.resolution_date
            if self.resolution_date != "None"
            else None,
            "url": self.browse_url(jira_url, self.key),
            "epic": self._epic_to_json(jira_url),
            "epic_text": f"{self.epic_key} \u2014 {self.epic_summary}"
            if self.epic_key
            else None,
            "sprint": self.sprint,
            "parent": self._parent_to_json(jira_url),
            "parent_text": f"{self.parent_key} \u2014 {self.parent_summary}"
            if self.parent_key
            else None,
            "subtasks": self._subtasks_to_json(),
            "story_points": self.story_points,
            "tags": self.tags if self.tags else None,
            "description": self.description_html or self.description_text,
            "description_text": self.description_text,
            "comments": self._comments_to_json(),
            "related_tasks": self._related_tasks_to_json(jira_url),
            "attachments": self._attachments_to_json(),
            "paths": {
                "raw": f"{download_path_rel}/{self.key}/raw.md",
                "task_json": f"{download_path_rel}/{self.key}/task.json",
            },
        }

    def _subtasks_to_json(self) -> list[dict[str, Any]]:
        return [
            {
                "key": st.key,
                "summary": st.summary,
                "status": st.status or None,
                "issue_type": st.issue_type or None,
                "url": st.url,
            }
            for st in self.subtasks_detail
        ]

    def _comments_to_json(self) -> list[dict[str, Any]]:
        return [
            {
                "author": c.author,
                "created": c.created or None,
                "body": c.body_text[:500] if c.body_text else "",
                "body_text": c.body_text[:500] if c.body_text else "",
            }
            for c in self.comments
        ]

    def _attachments_to_json(self) -> list[dict[str, Any]]:
        return [
            {
                "filename": a.filename or None,
                "url": a.url or None,
                "mime_type": a.mime_type or None,
                "size": a.size,
                "created": a.created or None,
                "author": {"display_name": a.author_name} if a.author_name else None,
            }
            for a in self.attachments
        ]

    def _epic_to_json(self, jira_url: str) -> dict[str, Any] | None:
        if not self.epic_key:
            return None
        return {
            "key": self.epic_key,
            "summary": self.epic_summary or "",
            "url": self.browse_url(jira_url, self.epic_key),
        }

    def _parent_to_json(self, jira_url: str) -> dict[str, Any] | None:
        if not self.parent_key:
            return None
        return {
            "key": self.parent_key,
            "summary": self.parent_summary or "",
            "issue_type": self.parent_type or None,
            "url": self.browse_url(jira_url, self.parent_key),
        }

    def _related_tasks_to_json(self, jira_url: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for li in self.linked_issues:
            uniq = (li["key"], li["type"], li.get("mention_source", "issue_link"))
            if uniq in seen:
                continue
            seen.add(uniq)
            result.append(
                {
                    "key": li["key"],
                    "summary": li.get("summary", ""),
                    "relation_type": li["type"],
                    "source": li.get("mention_source", "issue_link"),
                    "status": li.get("status") or None,
                    "issue_type": li.get("issue_type") or None,
                    "url": self.browse_url(jira_url, li["key"]),
                }
            )
        return result
