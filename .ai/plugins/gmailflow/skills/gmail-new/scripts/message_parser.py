"""Utilities for extracting readable message summaries from Gmail API payloads."""

from __future__ import annotations

import base64
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Any


def header_map(headers: list[dict[str, str]]) -> dict[str, str]:
    """Convert Gmail header lists into a simple name-to-value lookup."""
    return {item.get("name", ""): item.get("value", "") for item in headers}


def parse_datetime(value: str) -> str | None:
    """Normalize RFC email dates into local ISO timestamps when possible."""
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().isoformat(timespec="minutes")
    except Exception:
        return None


def decode_body(data: str | None) -> str:
    """Decode a base64url Gmail body fragment into text."""
    if not data:
        return ""
    try:
        decoded = base64.urlsafe_b64decode(data.encode("utf-8"))
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return ""


def find_plain_text(payload: dict[str, Any]) -> str:
    """Traverse nested payload parts and return the first plain-text body."""
    mime_type = payload.get("mimeType")
    body = payload.get("body", {})
    if mime_type == "text/plain":
        return decode_body(body.get("data"))
    for part in payload.get("parts", []) or []:
        text = find_plain_text(part)
        if text:
            return text
    return ""


def summarize_message(message: dict[str, Any]) -> dict[str, Any]:
    """Extract the fields GmailFlow uses for CLI and JSON summaries."""
    payload = message.get("payload", {})
    headers = header_map(payload.get("headers", []))
    snippet = (message.get("snippet") or "").strip()
    body_text = find_plain_text(payload).strip()
    body_preview = body_text[:400].strip() if body_text else ""
    label_ids = message.get("labelIds", [])

    return {
        "id": message.get("id"),
        "thread_id": message.get("threadId"),
        "subject": headers.get("Subject", "(no subject)"),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "date": parse_datetime(headers.get("Date", "")),
        "snippet": snippet,
        "body_preview": body_preview,
        "label_ids": label_ids,
        "importance": "high" if "IMPORTANT" in label_ids else "normal",
        "unread": "UNREAD" in label_ids,
    }
