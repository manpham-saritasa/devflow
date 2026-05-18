"""GitHub PR orchestration for Jira tasks.

Fetches linked PRs from Jira dev-status API,
renders markdown, and writes pr.md alongside raw.md.
"""

import os
import re
from typing import Any

from fetcher import fetch_issue_dev_status
from github_client import (
    fetch_pr_details,
    fetch_pr_files,
    fetch_pr_review_comments,
)
from github_pr_formatter import PRFormatter


def render_pr_md(
    pr_details: dict[str, Any],
    files: list[dict[str, Any]],
    review_comments: list[dict[str, Any]],
    task_key: str,
    github_repo: str,
) -> str:
    return PRFormatter().render(
        pr_details, files, review_comments, task_key, github_repo
    )


_PR_HEADER_RE = re.compile(r"^# PR #(\d+) —", re.MULTILINE)


def _existing_pr_numbers(filepath: str) -> set[str]:
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError:
        return set()
    return set(_PR_HEADER_RE.findall(content))


def fetch_and_write_pr(
    issue_data: dict[str, Any],
    download_path: str,
    force: bool = False,
) -> str:
    task_key = str(issue_data.get("key", ""))
    folder = os.path.join(download_path, task_key)
    pr_md_path = os.path.join(folder, "pr.md")

    # numeric id from Jira API response
    issue_id_str = str(issue_data.get("id", ""))
    if not issue_id_str.isdigit():
        print(f"    pr.md: no valid issue ID in response")
        return "error"

    linked_prs = fetch_issue_dev_status(int(issue_id_str))
    if not linked_prs:
        if not os.path.exists(pr_md_path):
            print(f"    pr.md: no linked PRs found")
        else:
            print(f"    pr.md: no new linked PRs (existing file kept)")
        return "no_pr"

    existing_numbers = set() if force else _existing_pr_numbers(pr_md_path)

    new_entries: list[tuple[str, str]] = []
    for pr_info in linked_prs:
        pr_number = pr_info["number"]
        repo = pr_info["repo"]

        if pr_number in existing_numbers and not force:
            print(f"    pr.md: PR #{pr_number} already in file - skipped")
            continue

        details = fetch_pr_details(int(pr_number), repo)
        if not details:
            continue
        files = fetch_pr_files(int(pr_number), repo)
        review_comments = fetch_pr_review_comments(int(pr_number), repo)
        entry = render_pr_md(details, files, review_comments, task_key, repo)
        new_entries.append((pr_number, entry))

    new_entries.sort(key=lambda x: int(x[0]))

    if not new_entries:
        if not os.path.exists(pr_md_path):
            print(f"    pr.md: error fetching details")
            return "error"
        print(f"    pr.md: all PRs already in file - nothing to do")
        return "skipped"

    os.makedirs(folder, exist_ok=True)
    tmp_path = pr_md_path + ".tmp"

    if force or not os.path.exists(pr_md_path):
        content = "\n\n---\n\n".join(entry for _, entry in new_entries) + "\n"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp_path, pr_md_path)
        pns = ", ".join(f"#{n}" for n, _ in new_entries)
        print(f"    pr.md: created ({len(new_entries)} PR(s): {pns})")
        return "created"
    else:
        try:
            with open(pr_md_path, "r", encoding="utf-8") as fh:
                existing = fh.read().rstrip("\n")
        except OSError:
            existing = ""
        content = (
            existing
            + "\n\n---\n\n"
            + "\n\n---\n\n".join(entry for _, entry in new_entries)
            + "\n"
        )
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp_path, pr_md_path)
        pns = ", ".join(f"#{n}" for n, _ in new_entries)
        print(f"    pr.md: appended ({len(new_entries)} new PR(s): {pns})")
        return "appended"
