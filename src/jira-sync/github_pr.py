"""GitHub PR orchestration for Jira tasks.

Searches PRs via github_client, matches by task key,
renders markdown, and writes pr.md alongside raw.md.
"""

import os
import re
from typing import Any

from github_client import (
    fetch_pr_details,
    fetch_pr_files,
    fetch_pr_review_comments,
    search_prs,
)
from github_pr_formatter import PRFormatter


def _extract_key_from_ref(head_ref: str, task_key: str) -> bool:
    return task_key.lower() in head_ref.lower()


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
    task_key: str,
    download_path: str,
    github_repo: str,
    force: bool = False,
) -> str:
    folder = os.path.join(download_path, task_key)
    pr_md_path = os.path.join(folder, "pr.md")

    raw_results = search_prs(task_key, github_repo)
    if not raw_results:
        if not os.path.exists(pr_md_path):
            print(f"    pr.md: no PR found")
        else:
            print(f"    pr.md: no new PR found (existing file kept)")
        return "no_pr"

    matched = []
    for pr in raw_results:
        head_ref = pr.get("headRefName") or ""
        title = pr.get("title") or ""
        if _extract_key_from_ref(head_ref, task_key) or _extract_key_from_ref(
            title, task_key
        ):
            matched.append(pr)

    existing_numbers = set() if force else _existing_pr_numbers(pr_md_path)

    new_entries: list[tuple[str, str]] = []
    for pr_summary in matched:
        pr_number = pr_summary.get("number")
        if not pr_number:
            continue
        pr_number_str = str(pr_number)

        if pr_number_str in existing_numbers and not force:
            print(f"    pr.md: PR #{pr_number} already in file - skipped")
            continue

        details = fetch_pr_details(pr_number, github_repo)
        if not details:
            continue
        files = fetch_pr_files(pr_number, github_repo)
        review_comments = fetch_pr_review_comments(pr_number, github_repo)
        entry = render_pr_md(details, files, review_comments, task_key, github_repo)
        new_entries.append((pr_number_str, entry))

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
        pns = ", ".join(f"#{pn}" for pn, _ in new_entries)
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
        pns = ", ".join(f"#{pn}" for pn, _ in new_entries)
        print(f"    pr.md: appended ({len(new_entries)} new PR(s): {pns})")
        return "appended"
