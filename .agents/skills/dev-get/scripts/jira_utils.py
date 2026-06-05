"""Static utility methods for Jira data extraction, formatting, and ADF processing."""

import re
from typing import Any

from comment import Comment


class JiraUtils:
    """Namespace for Jira-related static helpers."""

    @staticmethod
    def format_seconds(seconds: int | None) -> str:
        if seconds is None:
            return "None"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    @staticmethod
    def html_to_text(value: str) -> str:
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

    @staticmethod
    def adf_to_text(node: Any) -> str:
        if isinstance(node, str):
            return node
        if isinstance(node, dict):
            t = node.get("type")
            if t == "text":
                return node.get("text", "")
            if t == "mention":
                return "@" + node.get("attrs", {}).get("text", "")
            if t == "hardBreak":
                return "\n"
            content = node.get("content", [])
            text = "".join(JiraUtils.adf_to_text(c) for c in content)
            if t in (
                "paragraph",
                "heading",
                "bulletList",
                "orderedList",
                "blockquote",
                "codeBlock",
            ):
                text += "\n\n"
            elif t == "listItem":
                text = "- " + text.strip() + "\n"
            return text
        if isinstance(node, list):
            return "".join(JiraUtils.adf_to_text(i) for i in node)
        return ""

    @staticmethod
    def extract_subtask_keys(fields: dict[str, Any]) -> list[str]:
        return [
            s.get("key", "") for s in (fields.get("subtasks") or []) if s.get("key")
        ]

    @staticmethod
    def extract_comments(fields: dict[str, Any]) -> list[Comment]:
        result = []
        for c in (fields.get("comment") or {}).get("comments") or []:
            body = c.get("body", "")
            text = JiraUtils.adf_to_text(body) if isinstance(body, dict) else str(body)
            result.append(
                Comment(
                    author=str((c.get("author") or {}).get("displayName", "?")),
                    created=(c.get("created") or "?")[:10],
                    body_text=text,
                )
            )
        return result

    @staticmethod
    def extract_sprint(fields: dict[str, Any], sprint_field: str) -> str | None:
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
