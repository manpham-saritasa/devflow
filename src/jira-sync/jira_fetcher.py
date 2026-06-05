"""Reusable Jira task fetcher with typed return values and ADF extraction."""

import base64
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request as HttpRequest
from urllib.request import urlopen

from jira_extract import (
    Comment,
    adf_to_text,
    extract_comments,
    extract_subtask_keys,
)

# Re-export for convenience
__all__ = [
    "JiraTask",
    "JiraTaskFetcher",
    "FetcherConfig",
    "render_raw_md",
    "build_task_json",
]

DEFAULT_FIELDS = [
    "summary",
    "priority",
    "components",
    "description",
    "status",
    "issuetype",
    "assignee",
    "reporter",
    "labels",
    "fixVersions",
    "created",
    "updated",
    "duedate",
    "resolution",
    "resolutiondate",
    "parent",
    "subtasks",
    "issuelinks",
    "comment",
    "timetracking",
    "attachment",
]

_BUILTIN_TEMPLATE = """\
# {key} \u2014 {summary}

- **Status:** {status}
- **Type:** {issuetype}
- **Priority:** {priority}
- **Estimated:** {estimated}
- **Spent:** {spent}
- **Assignee:** {assignee}
- **Reporter:** {reporter}
- **Components:** {components}
- **Labels:** {labels}
- **Tags:** {tags}
- **Fix Versions:** {fix_versions}
- **Created:** {created}
- **Updated:** {updated}
- **Due Date:** {due_date}
- **Resolution:** {resolution}
- **Resolved At:** {resolution_date}
- **URL:** {url}

---

## Hierarchy

- **Epic:** {epic}
- **Sprint:** {sprint}
- **Parent:** {parent}
- **Story Points:** {story_points}
- **Subtasks:**{subtasks}

---

## Related Tasks

{related_tasks}

---

## Attachments

{attachments}

---

## Description

{description}

---

## Comments

{comments}
"""


@dataclass
class SubtaskInfo:
    key: str
    summary: str
    status: str
    issue_type: str | None
    url: str


@dataclass
class ParentInfo:
    key: str
    summary: str
    status: str
    issue_type: str | None
    url: str


@dataclass
class AttachmentInfo:
    filename: str
    url: str
    mime_type: str | None = None
    size: int | None = None
    created: str | None = None
    author_name: str | None = None


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
        return ""  # set externally or via fetcher

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
        link = f"[{self.epic_key}]({jira_url}/browse/{self.epic_key})"
        summary = self.epic_summary or ""
        return f"{link} \u2014 {summary}" if summary else link

    def sprint_md(self) -> str:
        return self.sprint or "None"

    def parent_md(self, jira_url: str = "") -> str:
        if not self.parent_key:
            return "None"
        link = f"[{self.parent_key}]({jira_url}/browse/{self.parent_key})"
        ptype = f" ({self.parent_type})" if self.parent_type else ""
        return f"{link} \u2014 {self.parent_summary}{ptype}"

    def subtasks_md(self, jira_url: str = "") -> str:
        if not self.subtasks_detail:
            return " None"
        items = sorted(self.subtasks_detail, key=lambda s: s.summary.lower())
        lines = []
        for st in items:
            lines.append(
                f"  - [{st.key}]({jira_url}/browse/{st.key}):"
                f" {st.summary} [{st.status}]"
            )
        return "\n" + "\n".join(lines)

    def related_tasks_md(self, jira_url: str = "") -> str:
        if not self.linked_issues:
            return "_(none)_"
        lines = []
        for li in self.linked_issues:
            lines.append(
                f"- **{li['type']}** [{li['key']}]({jira_url}/browse/{li['key']}):"
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
        return _format_seconds(self.estimated_seconds)

    def spent_str(self) -> str:
        return _format_seconds(self.spent_seconds)

    def to_json_record(
        self, download_path_rel: str, jira_url: str = ""
    ) -> dict[str, Any]:
        """Produce the structured task.json record."""
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
            "url": f"{jira_url}/browse/{self.key}",
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
            "url": f"{jira_url}/browse/{self.epic_key}",
        }

    def _parent_to_json(self, jira_url: str) -> dict[str, Any] | None:
        if not self.parent_key:
            return None
        return {
            "key": self.parent_key,
            "summary": self.parent_summary or "",
            "issue_type": self.parent_type or None,
            "url": f"{jira_url}/browse/{self.parent_key}",
        }

    def _related_tasks_to_json(self, jira_url: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for li in self.linked_issues:
            uniq = (li["key"], li["type"], "issue_link")
            if uniq in seen:
                continue
            seen.add(uniq)
            result.append(
                {
                    "key": li["key"],
                    "summary": li.get("summary", ""),
                    "relation_type": li["type"],
                    "source": "issue_link",
                    "status": li.get("status") or None,
                    "issue_type": li.get("issue_type") or None,
                    "url": f"{jira_url}/browse/{li['key']}",
                }
            )
        return result


def _format_seconds(seconds: int | None) -> str:
    if seconds is None:
        return "None"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


def _html_to_text(value: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li\b[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _load_template(template_paths: list[Path] | None = None) -> str:
    if template_paths:
        for path in template_paths:
            if path.exists():
                return path.read_text(encoding="utf-8")
    return _BUILTIN_TEMPLATE


def _extract_sprint(fields: dict[str, Any], sprint_field: str) -> str | None:
    sprint_raw = fields.get(sprint_field) if sprint_field else None
    if not sprint_raw:
        return None
    if isinstance(sprint_raw, list):
        if not sprint_raw:
            return None
        latest = sprint_raw[-1]
        if isinstance(latest, dict):
            return latest.get("name") or None
        return str(latest).strip() or None
    if isinstance(sprint_raw, dict):
        return sprint_raw.get("name") or None
    return str(sprint_raw).strip() or None


def render_raw_md(
    task: JiraTask,
    jira_url: str = "",
    tags_field_id: str = "",
    template_paths: list[Path] | None = None,
) -> str:
    """Render JiraTask as a comprehensive raw.md markdown string."""
    template = _load_template(template_paths)

    description_text = task.description_text or ""
    description = (
        f"```\n{description_text}\n```" if description_text else "_(no description)_"
    )

    comments_md = "_(no comments)_"
    if task.comments:
        lines = []
        for c in task.comments:
            body = c.body_text[:500] if c.body_text else "_(empty comment)_"
            lines.append(f"**{c.author}** ({c.created}):\n\n```\n{body}\n```")
        comments_md = "\n\n---\n\n".join(lines)

    return (
        template.replace("{key}", task.key)
        .replace("{summary}", task.summary)
        .replace("{status}", task.status)
        .replace("{issuetype}", task.issuetype)
        .replace("{priority}", task.priority)
        .replace("{estimated}", task.estimated_str())
        .replace("{spent}", task.spent_str())
        .replace("{assignee}", task.assignee)
        .replace("{reporter}", task.reporter)
        .replace("{components}", task.component_str)
        .replace("{labels}", task.label_str)
        .replace("{tags}", task.tags_md(jira_url, tags_field_id))
        .replace("{fix_versions}", task.fix_version_str)
        .replace("{created}", task.created)
        .replace("{updated}", task.updated)
        .replace("{due_date}", task.due_date)
        .replace("{resolution}", task.resolution)
        .replace("{resolution_date}", task.resolution_date)
        .replace("{url}", f"{jira_url}/browse/{task.key}")
        .replace("{epic}", task.epic_md(jira_url))
        .replace("{sprint}", task.sprint_md())
        .replace("{parent}", task.parent_md(jira_url))
        .replace("{story_points}", task.story_points or "None")
        .replace("{subtasks}", task.subtasks_md(jira_url))
        .replace("{related_tasks}", task.related_tasks_md(jira_url))
        .replace("{attachments}", task.attachments_md())
        .replace("{description}", description)
        .replace("{comments}", comments_md)
    )


def build_task_json(
    task: JiraTask, download_path_rel: str, jira_url: str = ""
) -> dict[str, Any]:
    """Build structured task.json record from a JiraTask."""
    return task.to_json_record(download_path_rel, jira_url)


@dataclass
class FetcherConfig:
    domain: str
    email: str
    token: str
    project_key: str = ""
    fields: list[str] | None = None
    custom_fields: dict[str, str] | None = None
    template_paths: list[Path] | None = None
    timeout: int = 30


class JiraTaskFetcher:
    def __init__(self, config: FetcherConfig) -> None:
        self._domain = config.domain
        self._base_url = f"https://{config.domain}.atlassian.net"
        self._auth = base64.b64encode(
            f"{config.email}:{config.token}".encode()
        ).decode()
        self._project_key = config.project_key
        self._custom_fields = config.custom_fields or {}
        self._template_paths = config.template_paths or []
        self._timeout = config.timeout

        custom_ids = [
            fid
            for fid in [
                self._custom_fields.get("story_points", ""),
                self._custom_fields.get("sprint", ""),
                self._custom_fields.get("tags", ""),
            ]
            if fid
        ]
        self._fields = (config.fields or DEFAULT_FIELDS) + custom_ids

    @classmethod
    def from_env(cls, root_path: str | None = None) -> "JiraTaskFetcher":
        env = cls._load_env(root_path)
        base = root_path or os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )

        # Load config.json for custom fields and template paths
        config_json = cls._load_config_json(base)
        custom_fields = config_json.get("custom_fields", {})
        project_key = env.get("JIRA_PROJECT_KEY", "")

        template_paths: list[Path] = []
        for tp in config_json.get("template_paths", []):
            if isinstance(tp, str):
                p = Path(base) / tp
                if p.exists():
                    template_paths.append(p)

        return cls(
            FetcherConfig(
                domain=env.get("JIRA_COMPANY_DOMAIN", ""),
                email=env.get("JIRA_EMAIL", ""),
                token=env.get("JIRA_API_TOKEN", ""),
                project_key=project_key,
                custom_fields=custom_fields,
                template_paths=template_paths,
            )
        )

    @classmethod
    def _load_env(cls, root_path: str | None = None) -> dict[str, str]:
        env: dict[str, str] = {}
        base = root_path or os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        for fname in [".env.local", ".env"]:
            path = os.path.join(base, fname)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip().strip('"')
        return env

    @classmethod
    def _load_config_json(cls, root_path: str) -> dict[str, Any]:
        # Try .local/jira-sync/config.json first, then src/jira-sync/config.json
        for rel_path in [
            ".local/jira-sync/config.json",
            "src/jira-sync/config.json",
        ]:
            path = os.path.join(root_path, rel_path)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
        return {}

    @property
    def project_key(self) -> str:
        return self._project_key

    @property
    def custom_fields(self) -> dict[str, str]:
        return dict(self._custom_fields)

    def fetch(self, issue_key: str) -> JiraTask | None:
        url = f"{self._base_url}/rest/api/3/issue/{issue_key}"
        params: dict[str, str] = {"fields": ",".join(self._fields)}
        try:
            data = self._get(url, params)
        except HTTPError as e:
            if e.code == 404:
                return None
            raise
        fields = data.get("fields") or {}
        return self._build_task(issue_key, fields)

    def get_max_issue_id(self, project_key: str | None = None) -> int:
        pk = project_key or self._project_key
        url = f"{self._base_url}/rest/api/3/search/jql"
        payload = json.dumps(
            {
                "jql": f"project = {pk} ORDER BY id DESC",
                "maxResults": 1,
                "fields": ["summary"],
            }
        ).encode("utf-8")
        req = HttpRequest(url, data=payload, method="POST")
        req.add_header("Authorization", f"Basic {self._auth}")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=self._timeout) as resp:
            data = json.loads(resp.read())
        issues = data.get("issues", [])
        if not issues:
            return 0
        key = issues[0].get("key", "")
        prefix, sep, suffix = str(key).rpartition("-")
        if not sep or not prefix or not suffix.isdigit():
            return 0
        return int(suffix)

    def fetch_children(self, parent_key: str) -> list[JiraTask]:
        """Fetch child issues via JQL parent={key}."""
        url = f"{self._base_url}/rest/api/3/search/jql"
        payload = json.dumps(
            {
                "jql": f"parent={parent_key}",
                "maxResults": 100,
                "fields": ["summary", "status", "issuetype"],
            }
        ).encode("utf-8")
        req = HttpRequest(url, data=payload, method="POST")
        req.add_header("Authorization", f"Basic {self._auth}")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=self._timeout) as resp:
            data = json.loads(resp.read())
        issues = data.get("issues", [])
        result: list[JiraTask] = []
        for issue in issues:
            fields = issue.get("fields") or {}
            key = issue.get("key", "")
            result.append(
                JiraTask(
                    key=key,
                    summary=str(fields.get("summary") or "?"),
                    status=self._safe(fields, "status", "name", default="?"),
                    issuetype=self._safe(fields, "issuetype", "name", default="?"),
                    priority="?",
                    assignee="",
                    reporter="",
                    labels=[],
                    components=[],
                    fix_versions=[],
                    created="",
                    updated="",
                    due_date="None",
                    resolution="Unresolved",
                    resolution_date="None",
                    description_raw=None,
                    description_text="",
                )
            )
        return result

    def should_fetch_children(self, task: JiraTask) -> bool:
        """Only fetch children for Epics that don't already have subtasks."""
        if task.issuetype.lower() != "epic":
            return False
        if task.subtask_keys:
            return False
        return True

    def discover_fields(self, show_all: bool = False) -> None:
        """Fetch and display custom fields from Jira for config.json setup."""
        pk = self._project_key
        print(f"Discovering custom fields for project '{pk}'...")
        print()

        custom_names = self._fetch_field_names()
        if not custom_names:
            print("No issues found in project. Cannot discover fields.")
            return

        if show_all:
            self._print_all_fields(custom_names)
            return

        matched_ids = self._print_configured_fields(custom_names)
        self._print_unmatched_fields(custom_names, matched_ids)

    @staticmethod
    def _print_all_fields(custom_names: dict[str, str]) -> None:
        print(f"All {len(custom_names)} custom fields:")
        print()
        for field_id, field_name in sorted(custom_names.items()):
            print(f"  {field_name}")
            print(f"  -> {field_id}")
            print()

    def _print_configured_fields(self, custom_names: dict[str, str]) -> set[str]:
        """Print configured field mappings. Returns matched field IDs."""
        configured = self._custom_fields
        if not configured:
            return set()

        matched: set[str] = set()
        print("Configured custom fields:")
        print()
        for config_key, config_value in configured.items():
            if not config_value:
                print(f'  "{config_key}": "",  # NOT SET')
                continue
            if config_value.startswith("customfield_"):
                name = custom_names.get(config_value, "unknown")
                print(f'  "{config_key}": "{config_value}",  # {name}')
                matched.add(config_value)
            else:
                found = False
                for field_id, field_name in sorted(custom_names.items()):
                    if field_name.lower() == config_value.lower():
                        print(f'  "{config_key}": "{field_id}",  # {field_name}')
                        matched.add(field_id)
                        found = True
                        break
                if not found:
                    print(f'  "{config_key}": "",  # NOT FOUND: "{config_value}"')
        print()
        return matched

    @staticmethod
    def _print_unmatched_fields(
        custom_names: dict[str, str], matched_ids: set[str]
    ) -> None:
        unmatched = {
            fid: fname
            for fid, fname in sorted(custom_names.items())
            if fid not in matched_ids
        }
        if not unmatched:
            return
        label = (
            "Other custom fields"
            if matched_ids
            else f"All {len(unmatched)} custom fields"
        )
        print(f"{label}:")
        print()
        for field_id, field_name in unmatched.items():
            print(f"  # {field_name}")
            print(f"  # -> {field_id}")
            print()

    def _fetch_field_names(self) -> dict[str, str]:
        """Return customfield_XXX -> display name mapping from a sample issue."""
        pk = self._project_key
        url = f"{self._base_url}/rest/api/3/search/jql"
        payload = json.dumps(
            {
                "jql": f"project = {pk} ORDER BY created DESC",
                "maxResults": 1,
                "fields": ["summary"],
            }
        ).encode("utf-8")
        req = HttpRequest(url, data=payload, method="POST")
        req.add_header("Authorization", f"Basic {self._auth}")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=self._timeout) as resp:
            data = json.loads(resp.read())
        issues = data.get("issues", [])
        if not issues:
            return {}

        sample_key = issues[0]["key"]
        url2 = f"{self._base_url}/rest/api/3/issue/{sample_key}"
        req2 = HttpRequest(url2)
        req2.add_header("Authorization", f"Basic {self._auth}")
        req2.add_header("Accept", "application/json")
        with urlopen(req2, timeout=self._timeout) as resp:
            names = json.loads(resp.read()).get("names") or {}

        result: dict[str, str] = {}
        for field_id, field_name in names.items():
            if field_id.startswith("customfield_"):
                result[field_id] = str(field_name)
        return result

    def _build_task(self, issue_key: str, fields: dict[str, Any]) -> JiraTask:
        desc_raw = fields.get("description")
        description_html, description_text = self._extract_desc(desc_raw)

        tt = fields.get("timetracking") or {}
        est_seconds = tt.get("originalEstimateSeconds")
        spent_seconds = tt.get("timeSpentSeconds")

        sprint = _extract_sprint(fields, self._custom_fields.get("sprint", ""))
        story_points = fields.get(self._custom_fields.get("story_points", ""))
        story_points_str = None if story_points in (None, "") else str(story_points)
        tags = [str(v) for v in (fields.get(self._custom_fields.get("tags", "")) or [])]
        parent = self._extract_parent_info(fields)

        return JiraTask(
            key=issue_key,
            summary=str(fields.get("summary") or "?"),
            status=self._safe(fields, "status", "name", default="?"),
            priority=self._safe(fields, "priority", "name", default="?"),
            issuetype=self._safe(fields, "issuetype", "name", default="?"),
            assignee=self._safe(
                fields, "assignee", "displayName", default="Unassigned"
            ),
            reporter=self._safe(fields, "reporter", "displayName", default="Unknown"),
            labels=[str(l) for l in (fields.get("labels") or [])],
            components=[
                c["name"] for c in (fields.get("components") or []) if "name" in c
            ],
            fix_versions=[
                v["name"] for v in (fields.get("fixVersions") or []) if "name" in v
            ],
            created=(fields.get("created") or "?")[:10],
            updated=(fields.get("updated") or "?")[:10],
            due_date="None" if not fields.get("duedate") else str(fields["duedate"]),
            resolution=self._safe(fields, "resolution", "name", default="Unresolved"),
            resolution_date="None"
            if not fields.get("resolutiondate")
            else str(fields["resolutiondate"])[:10],
            description_raw=desc_raw if isinstance(desc_raw, dict) else None,
            description_text=description_text,
            description_html=description_html,
            estimated=tt.get("originalEstimate") or "None",
            spent=tt.get("timeSpent") or "None",
            estimated_seconds=est_seconds,
            spent_seconds=spent_seconds,
            epic_key=parent["parent_key"] if parent["is_epic"] else None,
            epic_summary=parent["parent_summary"] if parent["is_epic"] else None,
            sprint=sprint,
            story_points=story_points_str,
            parent_key=None if parent["is_epic"] else parent["parent_key"],
            parent_summary="" if parent["is_epic"] else parent["parent_summary"],
            parent_type=None if parent["is_epic"] else parent["parent_type"],
            tags=tags,
            subtask_keys=extract_subtask_keys(fields),
            subtasks_detail=self._build_subtask_details(fields),
            linked_issues=self._build_linked_issues(fields),
            comments=extract_comments(fields),
            attachments=self._build_attachment_details(fields),
        )

    @staticmethod
    def _extract_desc(desc_raw: Any) -> tuple[str, str]:
        """Return (description_html, description_text) from raw Jira field."""
        html = ""
        if isinstance(desc_raw, str) and desc_raw:
            html = desc_raw
        if isinstance(desc_raw, dict):
            return html, adf_to_text(desc_raw)
        if isinstance(desc_raw, str):
            return html, desc_raw
        return html, "_(no description)_"

    @staticmethod
    def _extract_parent_info(fields: dict[str, Any]) -> dict[str, Any]:
        """Extract parent fields, distinguishing epic vs regular parent."""
        parent_raw = fields.get("parent") or {}
        parent_fields = parent_raw.get("fields") or {}
        parent_key = str(parent_raw.get("key") or "").strip() or None
        parent_summary = str(parent_fields.get("summary") or "").strip()
        parent_type = (
            str((parent_fields.get("issuetype") or {}).get("name", "")).strip() or None
        )
        return {
            "parent_key": parent_key,
            "parent_summary": parent_summary,
            "parent_type": parent_type,
            "is_epic": bool(parent_type and parent_type.lower() == "epic"),
        }

    def _build_subtask_details(self, fields: dict[str, Any]) -> list[SubtaskInfo]:
        result: list[SubtaskInfo] = []
        for st in fields.get("subtasks") or []:
            st_key = str(st.get("key") or "").strip()
            if not st_key:
                continue
            sf = st.get("fields") or {}
            result.append(
                SubtaskInfo(
                    key=st_key,
                    summary=str(sf.get("summary") or "").strip(),
                    status=str(((sf.get("status") or {}).get("name") or "")).strip(),
                    issue_type=str(
                        ((sf.get("issuetype") or {}).get("name") or "")
                    ).strip()
                    or None,
                    url=f"{self._base_url}/browse/{st_key}",
                )
            )
        return result

    def _build_linked_issues(self, fields: dict[str, Any]) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for link in fields.get("issuelinks") or []:
            for direction in ("inwardIssue", "outwardIssue"):
                issue = link.get(direction) or {}
                if not issue.get("key"):
                    continue
                issue_fields = issue.get("fields") or {}
                result.append(
                    {
                        "key": str(issue["key"]),
                        "summary": str(issue_fields.get("summary", "?")),
                        "type": str(
                            (link.get("type") or {}).get(
                                direction.replace("Issue", ""), "?"
                            )
                        ),
                        "status": str(
                            ((issue_fields.get("status") or {}).get("name") or "")
                        ),
                    }
                )
        return result

    def _build_attachment_details(self, fields: dict[str, Any]) -> list[AttachmentInfo]:
        result: list[AttachmentInfo] = []
        for att in fields.get("attachment") or []:
            filename = str(att.get("filename") or "").strip()
            content = str(att.get("content") or "").strip()
            if not filename and not content:
                continue
            author = att.get("author") if isinstance(att.get("author"), dict) else {}
            result.append(
                AttachmentInfo(
                    filename=filename or "",
                    url=content or "",
                    mime_type=str(att.get("mimeType") or "").strip() or None,
                    size=att.get("size"),
                    created=str(att.get("created") or "")[:10] or None,
                    author_name=str(author.get("displayName") or "").strip() or None,
                )
            )
        return result
