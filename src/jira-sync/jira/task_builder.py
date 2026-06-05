"""Builds JiraTask from raw Jira API field dicts."""

from typing import Any

from dto.attachment_info import AttachmentInfo
from dto.jira_task import JiraTask
from dto.subtask_info import SubtaskInfo

from jira.http_client import JiraHttpClient
from jira.jira_utils import JiraUtils


class JiraTaskBuilder:
    """Static factory that maps Jira API field dicts to JiraTask instances."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def build(
        self, issue_key: str, fields: dict[str, Any], custom_fields: dict[str, str]
    ) -> JiraTask:
        desc_raw = fields.get("description")
        description_html, description_text = self._extract_desc(desc_raw)
        tt = fields.get("timetracking") or {}
        est_seconds = tt.get("originalEstimateSeconds")
        spent_seconds = tt.get("timeSpentSeconds")
        sprint = JiraUtils.extract_sprint(fields, custom_fields.get("sprint", ""))
        story_points = fields.get(custom_fields.get("story_points", ""))
        story_points_str = None if story_points in (None, "") else str(story_points)
        tags = [str(v) for v in (fields.get(custom_fields.get("tags", "")) or [])]
        parent = self._extract_parent_info(fields)
        comments = JiraUtils.extract_comments(fields)
        safe = JiraHttpClient.safe_nav
        return JiraTask(
            key=issue_key,
            summary=str(fields.get("summary") or "?"),
            status=safe(fields, "status", "name", default="?"),
            priority=safe(fields, "priority", "name", default="?"),
            issuetype=safe(fields, "issuetype", "name", default="?"),
            assignee=safe(fields, "assignee", "displayName", default="Unassigned"),
            reporter=safe(fields, "reporter", "displayName", default="Unknown"),
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
            resolution=safe(fields, "resolution", "name", default="Unresolved"),
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
            subtask_keys=JiraUtils.extract_subtask_keys(fields),
            subtasks_detail=self._build_subtask_details(fields),
            linked_issues=self._build_linked_issues(fields)
            + self._extract_text_mentions(issue_key, description_text, comments),
            comments=comments,
            attachments=self._build_attachment_details(fields),
        )

    @staticmethod
    def _extract_desc(desc_raw: Any) -> tuple[str, str]:
        html = ""
        if isinstance(desc_raw, str) and desc_raw:
            html = desc_raw
        if isinstance(desc_raw, dict):
            return html, JiraUtils.adf_to_text(desc_raw)
        if isinstance(desc_raw, str):
            return html, desc_raw
        return html, "_(no description)_"

    @staticmethod
    def _extract_text_mentions(
        own_key: str, description_text: str, comments: list[Any]
    ) -> list[dict[str, str]]:
        """Extract issue keys mentioned in description and comment text."""
        import re

        key_re = re.compile(r"([A-Z][A-Z0-9]+)-(\d+)")
        seen: set[str] = set()
        result: list[dict[str, str]] = []
        sources: list[tuple[str, str]] = []
        if description_text:
            for m in key_re.finditer(description_text):
                if m.group(0) != own_key:
                    sources.append((m.group(0), "description"))
        for c in comments:
            body = getattr(c, "body_text", "") or ""
            for m in key_re.finditer(body):
                if m.group(0) != own_key:
                    sources.append((m.group(0), "comment"))
        for key, source in sources:
            if key not in seen:
                seen.add(key)
                result.append(
                    {
                        "key": key,
                        "summary": "",
                        "type": "mentioned",
                        "status": "?",
                        "mention_source": source,
                    }
                )
        return result

    @staticmethod
    def _extract_parent_info(fields: dict[str, Any]) -> dict[str, Any]:
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

    @staticmethod
    def _build_linked_issues(fields: dict[str, Any]) -> list[dict[str, str]]:
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

    @staticmethod
    def _build_attachment_details(fields: dict[str, Any]) -> list[AttachmentInfo]:
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
