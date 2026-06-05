"""Jira task fetcher — composes HTTP client, task builder, and field discoverer."""

import base64
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

from dto.fetcher_config import FetcherConfig
from dto.jira_task import JiraTask

from jira.field_discoverer import JiraFieldDiscoverer
from jira.http_client import JiraHttpClient
from jira.task_builder import JiraTaskBuilder

DEFAULT_FIELDS = [
    "summary",
    "priority",
    "components",
    "description",
    "status",
    "issuetype",
    "assignee",
    "reporter",
    "labels",
    "fixVersions",
    "created",
    "updated",
    "duedate",
    "resolution",
    "resolutiondate",
    "parent",
    "subtasks",
    "issuelinks",
    "comment",
    "timetracking",
    "attachment",
]


class JiraTaskFetcher:
    """Fetches Jira issues via REST API and builds typed JiraTask objects."""

    def __init__(self, config: FetcherConfig) -> None:
        self._domain = config.domain
        base_url = f"https://{config.domain}.atlassian.net"
        self._auth = base64.b64encode(
            f"{config.email}:{config.token}".encode()
        ).decode()
        self._project_key = config.project_key
        self._custom_fields = config.custom_fields or {}
        self._template_paths = config.template_paths or []
        self._timeout = config.timeout

        custom_ids = [
            fid
            for fid in [
                self._custom_fields.get("story_points", ""),
                self._custom_fields.get("sprint", ""),
                self._custom_fields.get("tags", ""),
            ]
            if fid
        ]
        self._fields = (config.fields or DEFAULT_FIELDS) + custom_ids
        self._http = JiraHttpClient(base_url, self._auth, self._timeout)
        self._builder = JiraTaskBuilder(base_url)

    @classmethod
    def from_env(cls, root_path: str | None = None) -> "JiraTaskFetcher":
        base = root_path or JiraHttpClient.find_repo_root()
        config_json, config_dir = cls._load_config_json(base)
        env_path = str(Path(config_dir) / config_json.get("env_path", ".env.local"))
        env = cls._load_env(base, env_path)
        custom_fields = config_json.get("custom_fields", {})
        project_key = env.get("JIRA_PROJECT_KEY", "")
        template_paths: list[Path] = []
        for tp in config_json.get("template_paths", []):
            if isinstance(tp, str):
                p = Path(base) / tp
                if p.exists():
                    template_paths.append(p)
        return cls(
            FetcherConfig(
                domain=env.get("JIRA_COMPANY_DOMAIN", ""),
                email=env.get("JIRA_EMAIL", ""),
                token=env.get("JIRA_API_TOKEN", ""),
                project_key=project_key,
                custom_fields=custom_fields,
                template_paths=template_paths,
            )
        )

    @classmethod
    def _load_env(cls, root_path: str, env_path: str) -> dict[str, str]:
        env: dict[str, str] = {}
        base = root_path
        for fname in [env_path, os.path.join(base, ".env")]:
            path = os.path.join(base, fname)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip().strip('"')
        return env

    @classmethod
    def _load_config_json(cls, root_path: str) -> tuple[dict[str, Any], str]:
        for rel_path in [".local/jira-sync/config.json", "src/jira-sync/config.json"]:
            path = os.path.join(root_path, rel_path)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data, os.path.dirname(path)
        return {}, ""

    @property
    def project_key(self) -> str:
        return self._project_key

    @property
    def custom_fields(self) -> dict[str, str]:
        return dict(self._custom_fields)

    def fetch(self, issue_key: str) -> JiraTask | None:
        url = f"{self._http.base_url}/rest/api/3/issue/{issue_key}"
        params: dict[str, str] = {"fields": ",".join(self._fields)}
        try:
            data = self._http.get(url, params)
        except HTTPError as e:
            if e.code == 404:
                return None
            raise
        fields = data.get("fields") or {}
        issue_id = str(data.get("id", ""))
        return self._builder.build(issue_key, issue_id, fields, self._custom_fields)

    def get_max_issue_id(self, project_key: str | None = None) -> int:
        pk = project_key or self._project_key
        data = self._http.post_json(
            f"{self._http.base_url}/rest/api/3/search/jql",
            {
                "jql": f"project = {pk} ORDER BY id DESC",
                "maxResults": 1,
                "fields": ["summary"],
            },
        )
        issues = data.get("issues", [])
        if not issues:
            return 0
        key = issues[0].get("key", "")
        prefix, sep, suffix = str(key).rpartition("-")
        if not sep or not prefix or not suffix.isdigit():
            return 0
        return int(suffix)

    def fetch_children(self, parent_key: str) -> list[JiraTask]:
        data = self._http.post_json(
            f"{self._http.base_url}/rest/api/3/search/jql",
            {
                "jql": f"parent={parent_key}",
                "maxResults": 100,
                "fields": ["summary", "status", "issuetype"],
            },
        )
        issues = data.get("issues", [])
        result: list[JiraTask] = []
        safe = JiraHttpClient.safe_nav
        for issue in issues:
            fields = issue.get("fields") or {}
            key = issue.get("key", "")
            result.append(
                JiraTask(
                    key=key,
                    summary=str(fields.get("summary") or "?"),
                    status=safe(fields, "status", "name", default="?"),
                    issuetype=safe(fields, "issuetype", "name", default="?"),
                    priority="?",
                    assignee="",
                    reporter="",
                    labels=[],
                    components=[],
                    fix_versions=[],
                    created="",
                    updated="",
                    due_date="None",
                    resolution="Unresolved",
                    resolution_date="None",
                    description_raw=None,
                    description_text="",
                )
            )
        return result

    def should_fetch_children(self, task: JiraTask) -> bool:
        if task.issuetype.lower() != "epic":
            return False
        if task.subtask_keys:
            return False
        return True

    def discover_fields(self, show_all: bool = False) -> None:
        discoverer = JiraFieldDiscoverer(
            self._http, self._project_key, self._custom_fields
        )
        discoverer.discover(show_all)
