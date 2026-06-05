"""HTTP client for Jira REST API v3."""

import json
import os
from typing import Any
from urllib.request import Request as HttpRequest
from urllib.request import urlopen


class JiraHttpClient:
    """Low-level HTTP GET/POST with Basic auth for Jira API."""

    def __init__(self, base_url: str, auth: str, timeout: int = 30) -> None:
        self._base_url = base_url
        self._auth = auth
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        return self._base_url

    def get(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        from urllib.parse import urlencode

        if params:
            url = f"{url}?{urlencode(params)}"
        req = HttpRequest(url)
        req.add_header("Authorization", f"Basic {self._auth}")
        req.add_header("Accept", "application/json")
        with urlopen(req, timeout=self._timeout) as resp:
            return json.loads(resp.read())

    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        req = HttpRequest(url, data=json.dumps(payload).encode("utf-8"), method="POST")
        req.add_header("Authorization", f"Basic {self._auth}")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=self._timeout) as resp:
            return json.loads(resp.read())

    @staticmethod
    def safe_nav(data: dict[str, Any], *keys: str, default: str = "?") -> str:
        """Navigate nested dicts, returning default if any key is missing."""
        for key in keys:
            if not isinstance(data, dict):
                return default
            data = data.get(key, {})
        return str(data) if data else default

    @staticmethod
    def find_repo_root() -> str:
        """Walk up from this file until a .git directory is found."""
        current = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            if os.path.isdir(os.path.join(current, ".git")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        raise RuntimeError("Could not find repository root (.git directory)")
