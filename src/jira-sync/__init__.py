"""jira-sync — fetch Jira issues as structured data with optional PR enrichment."""

from jira.fetcher import build_task_json, render_raw_md
from jira.task_fetcher import JiraTaskFetcher


def fetch_task(key: str, jira_url: str = "") -> dict | None:
    """Fetch a single Jira issue and return raw.md + task.json data.

    Returns dict with keys: raw_md, task_json, task_key, task_summary, status.
    Returns None if the issue is not found.
    """
    fetcher = JiraTaskFetcher.from_env()
    task = fetcher.fetch(key)
    if task is None:
        return None
    tags_field = fetcher.custom_fields.get("tags", "")
    return {
        "raw_md": render_raw_md(task, jira_url=jira_url, tags_field_id=tags_field),
        "task_json": build_task_json(task, "", jira_url),
        "task_key": task.key,
        "task_summary": task.summary,
        "status": task.status,
    }
