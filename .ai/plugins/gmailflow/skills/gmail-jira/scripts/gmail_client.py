"""Gmail helpers for reading full messages, attachments, and reply drafts."""

from __future__ import annotations

import base64
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request  # type: ignore[reportMissingImports]
from google.oauth2.credentials import Credentials  # type: ignore[reportMissingImports]
from googleapiclient.discovery import build  # type: ignore[reportMissingImports]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


class GmailClient:
    """Wrap Gmail API access needed by the gmail-jira workflow."""

    def __init__(self, env: dict[str, str]):
        """Create a Gmail API client from repo-local Gmail OAuth env values."""
        self.user_id = env["GMAIL_ACCOUNT"]
        creds = Credentials(
            token=None,
            refresh_token=env["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=env["GOOGLE_CLIENT_ID"],
            client_secret=env["GOOGLE_CLIENT_SECRET"],
            scopes=SCOPES,
        )
        try:
            creds.refresh(Request())
        except Exception:
            raise RuntimeError(
                "Gmail auth failed - check GOOGLE_REFRESH_TOKEN in .env.gmail. "
                "Re-run get_refresh_token.py to generate a new token."
            )
        self.service = build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False,
        )

    def get_message(self, message_id: str) -> dict[str, Any]:
        """Fetch one full Gmail message by id."""
        return (
            self.service.users()
            .messages()
            .get(userId=self.user_id, id=message_id, format="full")
            .execute()
        )

    def get_attachment_bytes(self, message_id: str, attachment_id: str) -> bytes:
        """Fetch one Gmail attachment payload and return raw bytes."""
        data = (
            self.service.users()
            .messages()
            .attachments()
            .get(userId=self.user_id, messageId=message_id, id=attachment_id)
            .execute()
            .get("data", "")
        )
        return base64.urlsafe_b64decode(data.encode("utf-8"))

    def save_attachment(
        self,
        folder: Path,
        message_id: str,
        item: dict[str, str],
    ) -> Path:
        """Download one Gmail attachment part into a local temp file."""
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / item["filename"]
        target.write_bytes(self.get_attachment_bytes(message_id, item["attachment_id"]))
        return target

    def create_reply_draft(
        self,
        message: dict[str, Any],
        reply_body: str,
        recipient: str,
        subject: str,
        message_header_id: str,
        cc: str = "",
    ) -> dict[str, Any]:
        """Create one Gmail draft reply in the original message thread."""
        mime = MIMEText(reply_body)
        mime["To"] = recipient
        if cc:
            mime["Cc"] = cc
        mime["Subject"] = subject
        if message_header_id:
            mime["In-Reply-To"] = message_header_id
            mime["References"] = message_header_id
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
        draft = {"message": {"threadId": message.get("threadId"), "raw": raw}}
        return (
            self.service.users()
            .drafts()
            .create(userId=self.user_id, body=draft)
            .execute()
        )
