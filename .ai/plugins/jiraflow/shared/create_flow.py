"""Shared reusable Jira issue create flow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import JiraCreateConfigStore, load_env
from .jira_api import JiraClient

JIRA_VARS = ["JIRA_COMPANY_DOMAIN", "JIRA_EMAIL", "JIRA_API_TOKEN"]


def missing_vars(env: dict[str, str], keys: list[str]) -> list[str]:
    """Return missing required variables from one loaded env dict."""
    return [key for key in keys if not env.get(key)]


def load_jira_client(
    repo_root: Path,
) -> tuple[dict[str, str], JiraCreateConfigStore, JiraClient]:
    """Load Jira env, cache store, client for repo-local workflow."""
    jira_env = load_env(repo_root / ".env.jira")
    return jira_env, JiraCreateConfigStore(repo_root), JiraClient(jira_env)


def discover_fields(
    store: JiraCreateConfigStore,
    jira_client: JiraClient,
    project_key: str,
    issue_type_id: str,
) -> tuple[dict[str, str | None], list[str]]:
    """Load or discover Jira custom field ids needed for issue creation."""
    cached = store.load_jira_fields()
    project_cache = cached.get(project_key, {})
    if all(project_cache.get(key) for key in ["sprint", "estimate", "environment"]):
        return project_cache, []
    meta = jira_client.get_create_meta(project_key, issue_type_id)
    fields = meta["projects"][0]["issuetypes"][0]["fields"]
    project_cache: dict[str, str | None] = {
        "sprint": "",
        "estimate": "",
        "environment": "",
    }
    for field_id, info in fields.items():
        name = info.get("name", "").lower()
        if name == "sprint":
            project_cache["sprint"] = field_id
        elif "development estimate" in name:
            project_cache["estimate"] = field_id
        elif name == "environment":
            project_cache["environment"] = field_id
    cached[project_key] = project_cache
    store.save_jira_fields(cached)
    missing = [key for key, value in project_cache.items() if not value]
    return project_cache, missing


def choose_scrum_board(boards: dict[str, Any], project_key: str) -> dict[str, Any]:
    """Pick first scrum board tied to target Jira project."""
    for item in boards.get("values", []):
        location = item.get("location", {})
        if item.get("type") == "scrum" and location.get("projectKey") == project_key:
            return item
    return {}


def load_create_context(
    jira_client: JiraClient,
    store: JiraCreateConfigStore,
    project_key: str,
    issue_type_id: str,
) -> tuple[dict[str, Any] | None, dict[str, str | None], list[str]]:
    """Load active sprint and custom field metadata for issue creation."""
    board = choose_scrum_board(jira_client.get_project_boards(project_key), project_key)
    sprint = jira_client.get_active_sprint(board["id"]) if board.get("id") else None
    fields, missing = discover_fields(store, jira_client, project_key, issue_type_id)
    if not board:
        missing = ["scrum board", "active sprint", *missing]
    elif not sprint:
        missing = ["active sprint", *missing]
    return sprint, fields, missing


def _empty_adf() -> dict[str, Any]:
    """Minimal ADF doc when no description is provided."""
    return {"type": "doc", "version": 1, "content": []}


def _env_to_adf(text: str) -> dict[str, Any]:
    """Wrap plain environment text as Atlassian Document Format."""
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def build_issue_fields(proposal: dict[str, Any]) -> dict[str, Any]:
    """Build Jira issue create payload fields from proposal."""
    fields = {
        "project": {"key": proposal["project"]},
        "summary": proposal["summary"],
        "description": proposal.get("description") or _empty_adf(),
        "issuetype": {"id": proposal["issue_type"]["id"]},
        "components": [{"id": proposal["component"]["id"]}],
    }
    sprint = proposal.get("sprint") or {}
    add_custom_field(fields, proposal["jira_fields"].get("sprint"), sprint.get("id"))
    add_custom_field(
        fields,
        proposal["jira_fields"].get("estimate"),
        proposal["estimate_hours"],
    )
    env_field_id = proposal["jira_fields"].get("environment")
    env_value = proposal.get("environment")
    if env_field_id and env_value:
        fields[env_field_id] = (
            _env_to_adf(env_value) if env_field_id == "environment" else env_value
        )
    return fields


def add_custom_field(fields: dict[str, Any], field_id: str | None, value: Any) -> None:
    """Add optional custom field only when field id and value exist."""
    if field_id and value is not None:
        fields[field_id] = value


def create_issue_from_proposal(
    repo_root: Path, proposal: dict[str, Any]
) -> dict[str, Any]:
    """Create Jira issue from already-built proposal payload."""
    _, _, jira_client = load_jira_client(repo_root)
    return jira_client.create_issue(build_issue_fields(proposal))


def attach_files(
    repo_root: Path, issue_key: str, file_paths: list[Path]
) -> list[dict[str, Any]]:
    """Upload local files to Jira issue, one result per file."""
    _, _, jira_client = load_jira_client(repo_root)
    results: list[dict[str, Any]] = []
    for file_path in file_paths:
        uploaded = jira_client.attach_file(issue_key, file_path)
        results.append({"filename": file_path.name, "upload": uploaded})
    return results
