"""Email parsing helpers for gmail-jira generic proposal building."""

from __future__ import annotations

import base64
import binascii
from typing import Any

FORWARDED_MARKERS = [
    "From:",
    "Sent:",
    "Subject:",
    "-----Original Message-----",
    "Copyright (c)",
]
SIGNATURE_MARKERS = [
    "mobile:",
    "phone:",
    "fax:",
    "www.",
    ".com",
    "street",
    "court",
    "avenue",
    "drive",
]


def decode_body(data: str | None) -> str:
    """Decode one Gmail base64url body fragment into readable text."""
    if not data:
        return ""
    try:
        raw = base64.urlsafe_b64decode(data.encode("utf-8"))
        return raw.decode("utf-8", errors="replace")
    except (ValueError, binascii.Error):
        return ""


def extract_text(payload: dict[str, Any]) -> str:
    """Return first plain-text body found in nested Gmail parts."""
    if payload.get("mimeType") == "text/plain":
        return clean_body_text(decode_body(payload.get("body", {}).get("data")))
    for part in payload.get("parts", []) or []:
        text = extract_text(part)
        if text:
            return text
    return ""


def collect_attachments(
    payload: dict[str, Any],
    attachments: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Collect attachment metadata from nested Gmail message parts."""
    items = attachments if attachments is not None else []
    body = payload.get("body", {})
    filename = payload.get("filename", "")
    attachment_id = body.get("attachmentId", "")
    if filename and attachment_id:
        headers = payload.get("headers", [])
        items.append(
            {
                "filename": filename,
                "attachment_id": attachment_id,
                "mime_type": payload.get("mimeType", ""),
                "content_id": header_value(headers, "Content-ID"),
                "disposition": header_value(headers, "Content-Disposition"),
                "size": str(body.get("size", 0)),
            }
        )
    for part in payload.get("parts", []) or []:
        collect_attachments(part, items)
    return items


def header_value(headers: list[dict[str, str]], key: str) -> str:
    """Find one MIME header value by case-insensitive name."""
    target = key.lower()
    for item in headers:
        if item.get("name", "").lower() == target:
            return item.get("value", "")
    return ""


def classify_attachment(item: dict[str, str]) -> str:
    """Classify Gmail file parts into upload, skip, or review buckets."""
    filename = item.get("filename", "")
    disposition = item.get("disposition", "").lower()
    mime_type = item.get("mime_type", "")
    size = int(item.get("size", "0") or "0")
    if filename.lower() == "image001.png":
        return "skip"
    if "attachment" in disposition:
        return "upload"
    if mime_type.startswith("image/") and size < 10000:
        return "skip"
    return "review"


def split_before_markers(text: str) -> str:
    """Trim quoted history and legal/footer blocks using common email markers."""
    lines = text.splitlines()
    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(marker) for marker in FORWARDED_MARKERS):
            break
        kept.append(line)
    return "\n".join(kept)


def normalize_lines(text: str) -> list[str]:
    """Normalize body text into meaningful non-empty lines only."""
    items = [line.strip() for line in text.splitlines() if line.strip()]
    return [line for line in items if not line.startswith("[")]


def is_signature_line(line: str) -> bool:
    """Detect common signature or contact-detail lines in email bodies."""
    lower = line.lower()
    if any(marker in lower for marker in SIGNATURE_MARKERS):
        return True
    if line.endswith(", PE") or line.endswith(", P.E."):
        return True
    if "@" in line and " " not in line:
        return True
    if sum(char.isdigit() for char in line) >= 7:
        return True
    return False


def strip_signature(lines: list[str]) -> list[str]:
    """Trim trailing signature/contact lines after the main request text."""
    kept: list[str] = []
    for line in lines:
        if is_signature_line(line):
            break
        kept.append(line)
    return kept


def strip_greeting(lines: list[str]) -> list[str]:
    """Drop short greeting lines like 'Hi X' or bare names before the real ask."""
    if not lines:
        return []
    first = lines[0].lower().rstrip(",")
    if first.startswith("hi ") or first in {"quan", "team", "all"}:
        return lines[1:]
    return lines


def clean_body_text(text: str) -> str:
    """Reduce raw email body to the new content worth summarizing into Jira."""
    trimmed = split_before_markers(text)
    lines = normalize_lines(trimmed)
    lines = strip_greeting(lines)
    lines = strip_signature(lines)
    return "\n".join(lines)
