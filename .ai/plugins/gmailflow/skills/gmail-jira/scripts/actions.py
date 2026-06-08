"""Side-effect actions for gmail-jira: attachment upload and reply draft."""

from __future__ import annotations

import sys
from pathlib import Path

_JIRAFLOW_ROOT = Path(__file__).resolve().parents[4] / "jiraflow"
if str(_JIRAFLOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_JIRAFLOW_ROOT))

from typing import Any

from gmail_client import GmailClient
from shared.common import load_env
from shared.create_flow import attach_files


def upload_attachments(
    repo_root: Path,
    message_id: str,
    issue_key: str,
    attachments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Download approved Gmail attachments and upload them to Jira."""
    gmail_client = GmailClient(load_env(repo_root / ".env.gmail"))
    folder = repo_root / ".local" / "tmp" / "gmail-jira"
    file_paths = []
    for item in attachments:
        if item.get("action") != "upload":
            continue
        try:
            file_paths.append(gmail_client.save_attachment(folder, message_id, item))
        except OSError as exc:
            return [{"filename": item.get("filename", ""), "error": str(exc)}]
    return attach_files(repo_root, issue_key, file_paths)


def create_reply_draft(
    repo_root: Path,
    message_id: str,
    reply_body: str,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    """Create the Gmail draft reply after the Jira issue exists."""
    gmail_client = GmailClient(load_env(repo_root / ".env.gmail"))
    message = gmail_client.get_message(message_id)
    subject = proposal["message"]["subject"]
    subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    recipients = proposal["message"].get("reply_to_all", {})
    return gmail_client.create_reply_draft(
        message,
        reply_body,
        recipients.get("to", proposal["message"]["reply_to"]),
        subject,
        proposal["message"]["message_id_header"],
        cc=recipients.get("cc", ""),
    )
