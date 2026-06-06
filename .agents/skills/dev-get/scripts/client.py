"""Convenience import for external scripts like dev-get.

Usage:
    import sys; sys.path.insert(0, ".agents/skills/dev-get/scripts")
    from client import fetch_task

    result = fetch_task("RMASUP-2191")
    if result:
        print(result["raw_md"])
"""

import base64
import json
import os
from urllib.error import HTTPError

from dotenv import load_dotenv
from fetcher import build_task_json, render_raw_md
from http_client import JiraHttpClient
from task_builder import JiraTaskBuilder

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


def _load_config(root: str) -> dict:
    """Load jira-sync config.json, returning {} if not found."""
    for rel_path in [".local/jira-sync/config.json", "src/jira-sync/config.json"]:
        path = os.path.join(root, rel_path)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
    return {}


def fetch_task(key: str, jira_url: str = "") -> dict | None:
    """Fetch a single Jira issue.

    Returns dict: raw_md, task_json, task_key, task_summary, status.
    Returns None if not found.
    """
    root = JiraHttpClient.find_repo_root()

    load_dotenv(os.path.join(root, ".env.jira"))

    domain = os.environ.get("JIRA_COMPANY_DOMAIN", "")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    base_url = f"https://{domain}.atlassian.net"
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()

    http = JiraHttpClient(base_url, auth)
    builder = JiraTaskBuilder(base_url)

    config = _load_config(root)
    custom_fields = config.get("custom_fields", {})

    fields = list(DEFAULT_FIELDS)
    for fid in [
        custom_fields.get("story_points", ""),
        custom_fields.get("sprint", ""),
        custom_fields.get("tags", ""),
    ]:
        if fid:
            fields.append(fid)

    url = f"{base_url}/rest/api/3/issue/{key}"
    params: dict[str, str] = {"fields": ",".join(fields)}

    try:
        data = http.get(url, params)
    except HTTPError as e:
        if e.code == 404:
            return None
        raise

    fields_data = data.get("fields") or {}
    issue_id = str(data.get("id", ""))

    task = builder.build(key, issue_id, fields_data, custom_fields)

    tags_field = custom_fields.get("tags", "")

    return {
        "raw_md": render_raw_md(task, jira_url=jira_url, tags_field_id=tags_field),
        "task_json": build_task_json(task, "", jira_url),
        "task_key": task.key,
        "task_summary": task.summary,
        "status": task.status,
    }
