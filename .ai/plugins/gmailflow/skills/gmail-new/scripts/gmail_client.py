"""Gmail API client helpers for label discovery and message retrieval."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from google.auth.transport.requests import Request  # type: ignore[reportMissingImports]
from google.oauth2.credentials import Credentials  # type: ignore[reportMissingImports]
from googleapiclient.discovery import build  # type: ignore[reportMissingImports]
from message_parser import summarize_message
from project_labels import GmailProjectLabelStore

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _quote_label(label_name: str) -> str:
    """Quote Gmail label name for use in search query if it contains spaces."""
    if not label_name or not label_name.strip():
        return ""
    name = label_name.strip()
    return f'"{name}"' if " " in name else name


class GmailClient:
    """Wrap Gmail API calls used by the gmail-new CLI flow."""

    def __init__(self, env: dict[str, str]):
        """Create a Gmail client from validated environment configuration."""
        self.env = env
        self.user_id = env["GMAIL_ACCOUNT"]
        self.service = build(
            "gmail",
            "v1",
            credentials=self._make_credentials(),
            cache_discovery=False,
        )

    def list_labels(self) -> dict[str, str]:
        """Return the mailbox label name-to-id mapping."""
        response = self.service.users().labels().list(userId=self.user_id).execute()
        items = response.get("labels", [])
        return {
            item.get("name", ""): item.get("id", "")
            for item in items
            if item.get("name") and item.get("id")
        }

    def fetch_messages(self, query: str, max_results: int) -> dict[str, Any]:
        """Fetch recent messages without project-label filtering."""
        items = self._fetch_message_batch(query, max_results)
        return self._build_payload(query, max_results, items)

    def fetch_messages_by_project_labels(
        self,
        query: str,
        max_results: int,
        project_label_map: dict[str, dict[str, str]],
        label_store: GmailProjectLabelStore,
    ) -> dict[str, Any]:
        """Fetch messages grouped by configured project Gmail labels."""
        gmail_label_map = self.list_labels()
        project_label_map, updated_cache = label_store.resolve_label_ids(
            project_label_map, gmail_label_map
        )
        items: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        resolved_labels: dict[str, dict[str, str | None]] = {}

        for project, label_info in project_label_map.items():
            label_name = label_info.get("label_name", "")
            label_id = label_info.get("label_id") or gmail_label_map.get(label_name)
            resolved_labels[project] = {"label_name": label_name, "label_id": label_id}
            label_query = _quote_label(label_name)
            batch_query = f"{query} label:{label_query}" if label_query else query
            batch = self._fetch_message_batch(batch_query, max_results)
            self._merge_project_batch(
                items,
                seen_ids,
                batch,
                {"project": project, "label_name": label_name},
            )

        payload = self._build_payload(query, max_results, items)
        payload["project_label_filter"] = {
            key: value.get("label_name", "") for key, value in project_label_map.items()
        }
        payload["resolved_labels"] = resolved_labels
        payload["updated_project_labels"] = updated_cache
        return payload

    def _make_credentials(self) -> Credentials:
        """Build refreshable Gmail OAuth credentials from env values."""
        creds = Credentials(
            token=None,
            refresh_token=self.env["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.env["GOOGLE_CLIENT_ID"],
            client_secret=self.env["GOOGLE_CLIENT_SECRET"],
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return creds

    def _fetch_message_batch(
        self,
        query: str,
        max_results: int,
        label_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch and summarize one Gmail API message batch."""
        request = (
            self.service.users()
            .messages()
            .list(
                userId=self.user_id,
                q=query,
                maxResults=max_results,
                labelIds=label_ids or None,
            )
        )
        listed = request.execute()
        refs = listed.get("messages", [])
        items: list[dict[str, Any]] = []
        for ref in refs:
            full = (
                self.service.users()
                .messages()
                .get(
                    userId=self.user_id,
                    id=ref["id"],
                    format="full",
                )
                .execute()
            )
            items.append(summarize_message(full))
        return items

    def _merge_project_batch(
        self,
        items: list[dict[str, Any]],
        seen_ids: set[str],
        batch: list[dict[str, Any]],
        match_info: dict[str, str],
    ) -> None:
        """Merge a labeled batch into the deduplicated result set."""
        for item in batch:
            item_id = item.get("id")
            if not item_id or item_id in seen_ids:
                continue
            item["matched_projects"] = [match_info["project"]]
            item["matched_labels"] = [match_info["label_name"]]
            seen_ids.add(item_id)
            items.append(item)

    def _build_payload(
        self,
        query: str,
        max_results: int,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build the common JSON payload returned by GmailFlow reads."""
        return {
            "ok": True,
            "account": self.user_id,
            "query": query,
            "max_results": max_results,
            "count": len(items),
            "messages": items,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
