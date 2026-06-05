"""ADF text extraction and static field helpers for Jira data."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Comment:
    author: str
    created: str
    body_text: str


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
        text = "".join(adf_to_text(c) for c in content)
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
        return "".join(adf_to_text(i) for i in node)
    return ""


def extract_subtask_keys(fields: dict[str, Any]) -> list[str]:
    return [s.get("key", "") for s in (fields.get("subtasks") or []) if s.get("key")]


def extract_links(fields: dict[str, Any]) -> list[dict[str, str]]:
    result = []
    for link in fields.get("issuelinks") or []:
        for d in ("inwardIssue", "outwardIssue"):
            issue = link.get(d) or {}
            if issue.get("key"):
                result.append(
                    {
                        "key": str(issue["key"]),
                        "summary": str((issue.get("fields") or {}).get("summary", "?")),
                        "type": str(
                            link.get("type", {}).get(d.replace("Issue", ""), "?")
                        ),
                        "direction": d,
                    }
                )
    return result


def extract_attachments(fields: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"filename": a.get("filename", "?"), "url": a.get("content", "?")}
        for a in (fields.get("attachment") or [])
    ]


def extract_comments(fields: dict[str, Any]) -> list[Comment]:
    result = []
    for c in (fields.get("comment") or {}).get("comments") or []:
        body = c.get("body", "")
        text = adf_to_text(body) if isinstance(body, dict) else str(body)
        result.append(
            Comment(
                author=str((c.get("author") or {}).get("displayName", "?")),
                created=(c.get("created") or "?")[:10],
                body_text=text,
            )
        )
    return result
