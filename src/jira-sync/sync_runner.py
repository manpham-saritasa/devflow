"""Sync runner: single-task and range-sync orchestration."""

import json
import os
from pathlib import Path

from config import JIRA_URL, REPO_ROOT
from jira_fetcher import (
    JiraTask,
    JiraTaskFetcher,
    SubtaskInfo,
    build_task_json,
    render_raw_md,
)
from sync_state import add_not_found_id, save_state


def _get_fetcher() -> JiraTaskFetcher:
    """Create a JiraTaskFetcher from environment and config."""
    return JiraTaskFetcher.from_env(str(REPO_ROOT))


def _write_outputs(
    task: JiraTask,
    download_path: str,
    download_path_rel: str,
    force: bool,
    jira_url: str = "",
    tags_field_id: str = "",
) -> str:
    """Write raw.md and task.json for a JiraTask. Returns result string."""
    key = task.key
    task_dir = os.path.join(download_path, key)
    os.makedirs(task_dir, exist_ok=True)

    raw_path = os.path.join(task_dir, "raw.md")
    json_path = os.path.join(task_dir, "task.json")

    existed = os.path.exists(raw_path)
    if existed and not force:
        return "skipped"

    # Write raw.md
    raw_content = render_raw_md(task, jira_url=jira_url, tags_field_id=tags_field_id)
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_content)

    # Write task.json
    json_record = build_task_json(task, download_path_rel, jira_url)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_record, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return "overwritten" if existed else "created"


def _print_result(key: str, result: str, children_count: int) -> None:
    suffix = f" (with {children_count} children)" if children_count else ""
    if result == "not_found":
        print(f"  {key}: not found - added to skipped list")
        print()
    else:
        print(f"  {key}: {result}{suffix}")
        print()
    print("--- Done ---")
    if result == "not_found":
        print(
            "Created:     0\nOverwritten: 0\nSkipped:     0\n"
            "Not found:   1\nErrors:      0"
        )
    elif result == "error":
        print(
            "Created:     0\nOverwritten: 0\nSkipped:     0\n"
            "Not found:   0\nErrors:      1"
        )
    else:
        created = int(result == "created")
        overwritten = int(result == "overwritten")
        skipped = int(result == "skipped")
        print(f"Created:     {created}")
        print(f"Overwritten: {overwritten}")
        print(f"Skipped:     {skipped}")
        print("Not found:   0")
        print("Errors:      0")


def _fetch_children_for_task(fetcher: JiraTaskFetcher, task: JiraTask) -> int:
    """Fetch epic children into task.subtasks_detail. Returns child count."""
    if not fetcher.should_fetch_children(task):
        return 0
    key = task.key
    try:
        children = fetcher.fetch_children(key)
    except Exception as e:
        print(f"  {key}: ERROR fetching children - {e}")
        return 0
    for child in children:
        task.subtasks_detail.append(
            SubtaskInfo(
                key=child.key,
                summary=child.summary,
                status=child.status,
                issue_type=child.issuetype,
                url=child.url,
            )
        )
    return len(children)


def sync_one_issue(
    project_key: str,
    issue_id: int,
    force: bool,
    download_path: str,
    download_path_rel: str,
    not_found_state_path: Path,
    with_prs: bool = False,
) -> int:
    """Sync a single Jira issue to raw.md and task.json."""
    key = f"{project_key}-{issue_id}"
    print(f"Project:       {project_key}")
    print(f"Download path: {download_path}")
    print(f"Target:        {key}")
    print(f"Mode:          {'force overwrite' if force else 'skip existing'}")
    print()

    try:
        fetcher = _get_fetcher()
        task = fetcher.fetch(key)
        if task is None:
            add_not_found_id(not_found_state_path, project_key, issue_id)
            _print_result(key, "not_found", 0)
            return 0

        clen = _fetch_children_for_task(fetcher, task)
        tags_field = fetcher.custom_fields.get("tags", "")
        result = _write_outputs(
            task,
            download_path,
            download_path_rel,
            force,
            jira_url=JIRA_URL,
            tags_field_id=tags_field,
        )
        _print_result(key, result, clen)
        return 0
    except Exception as e:
        print(f"  {key}: ERROR - {e}")
        _print_result(key, "error", 0)
        return 1


def range_sync_issue(
    project_key: str,
    issue_id: int,
    force: bool,
    download_path: str,
    download_path_rel: str,
    sync_state_path: Path,
    not_found_state_path: Path,
    known_not_found_ids: set[str],
    not_sync: set[str],
    force_sync: set[str],
) -> tuple[str, int]:
    """Sync one issue during range sync. Returns (result, children_count)."""
    fetcher = _get_fetcher()
    key = f"{project_key}-{issue_id}"

    if key in not_sync:
        print(f"  {key}: in not-sync list - skip")
        save_state(sync_state_path, project_key, issue_id)
        return ("skipped", 0)
    if key in known_not_found_ids:
        print(f"  {key}: known missing - skip")
        save_state(sync_state_path, project_key, issue_id)
        return ("not_found", 0)

    effective_force = force or key in force_sync
    task = fetcher.fetch(key)
    if task is None:
        add_not_found_id(not_found_state_path, project_key, issue_id)
        print(f"  {key}: not found")
        save_state(sync_state_path, project_key, issue_id)
        return ("not_found", 0)

    clen = _fetch_children_for_task(fetcher, task)
    tags_field = fetcher.custom_fields.get("tags", "")
    result = _write_outputs(
        task,
        download_path,
        download_path_rel,
        effective_force,
        jira_url=JIRA_URL,
        tags_field_id=tags_field,
    )
    save_state(sync_state_path, project_key, issue_id)
    suffix = f" ({clen} children)" if clen else ""
    print(f"  {key}: {result}{suffix}")
    return (result, clen)
