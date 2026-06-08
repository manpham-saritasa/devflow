"""Shared Jira API helpers for metadata, issue creation, attachments."""

from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class JiraClient:
    """Wrap Jira REST calls used by JiraFlow workflows."""

    def __init__(self, env: dict[str, str]):
        """Build authenticated Jira request headers from repo-local env values."""
        auth = base64.b64encode(
            f"{env['JIRA_EMAIL']}:{env['JIRA_API_TOKEN']}".encode()
        ).decode()
        self.base_url = f"https://{env['JIRA_COMPANY_DOMAIN']}.atlassian.net"
        self.headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}

    def get_project(self, project_key: str) -> dict[str, Any]:
        """Fetch Jira project metadata including components and issue types."""
        return self._get_json(f"/rest/api/3/project/{project_key}")

    def get_active_sprint(self, board_id: int) -> dict[str, Any] | None:
        """Fetch first active sprint on selected scrum board."""
        data = self._get_json(f"/rest/agile/1.0/board/{board_id}/sprint?state=active")
        values = data.get("values", [])
        return values[0] if values else None

    def get_project_boards(self, project_key: str) -> dict[str, Any]:
        """Fetch Jira boards tied to chosen project."""
        return self._get_json(f"/rest/agile/1.0/board?projectKeyOrId={project_key}")

    def get_create_meta(self, project_key: str, issue_type_id: str) -> dict[str, Any]:
        """Fetch create metadata for one project and issue type."""
        query = urlencode(
            {
                "projectKeys": project_key,
                "issuetypeIds": issue_type_id,
                "expand": "projects.issuetypes.fields",
            }
        )
        return self._get_json(f"/rest/api/3/issue/createmeta?{query}")

    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]:
        """Create one Jira issue and return API response."""
        payload = json.dumps({"fields": fields}).encode()
        return self._post_json("/rest/api/3/issue", payload)

    def attach_file(self, issue_key: str, file_path: Path) -> dict[str, Any]:
        """Upload one file attachment to existing Jira issue."""
        boundary = "gmailjiraboundary"
        mime_type = (
            mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        )
        body = self._build_multipart(boundary, file_path, mime_type)
        headers = dict(self.headers)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        headers["X-Atlassian-Token"] = "no-check"
        request = Request(
            self.base_url + f"/rest/api/3/issue/{issue_key}/attachments",
            data=body,
            headers=headers,
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            return {"items": json.load(response)}

    def _get_json(self, path: str) -> dict[str, Any]:
        """Run one authenticated Jira GET request."""
        request = Request(self.base_url + path, headers=self.headers)
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    def _build_multipart(self, boundary: str, file_path: Path, mime_type: str) -> bytes:
        """Build one multipart form-data payload for Jira file upload."""
        header = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode()
        footer = f"\r\n--{boundary}--\r\n".encode()
        return header + file_path.read_bytes() + footer

    def _post_json(self, path: str, payload: bytes) -> dict[str, Any]:
        """Run one authenticated Jira POST request with JSON body."""
        headers = dict(self.headers)
        headers["Content-Type"] = "application/json"
        request = Request(
            self.base_url + path, data=payload, headers=headers, method="POST"
        )
        with urlopen(request, timeout=30) as response:
            return json.load(response)
