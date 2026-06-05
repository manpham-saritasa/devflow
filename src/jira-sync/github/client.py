"""GitHub API calls via gh CLI."""

import json
import subprocess
from typing import Any


def _gh_json(args: list[str], label: str = "") -> Any:
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, encoding="utf-8", timeout=60
        )
        if result.returncode != 0:
            if label:
                print(f"  [gh] {label}: {result.stderr.strip()[:200]}")
            return None
        return json.loads(result.stdout)
    except FileNotFoundError:
        print(
            "  [gh] ERROR: 'gh' CLI not found. Install from https://cli.github.com or remove --with-prs"
        )
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        if label:
            print(f"  [gh] {label}: {e}")
        return None


def _gh_lines(args: list[str], label: str = "") -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, encoding="utf-8", timeout=60
        )
        if result.returncode != 0:
            if label:
                print(f"  [gh] {label}: {result.stderr.strip()[:200]}")
            return []
        items = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return items
    except FileNotFoundError:
        print(
            "  [gh] ERROR: 'gh' CLI not found. Install from https://cli.github.com or remove --with-prs"
        )
        return []
    except subprocess.TimeoutExpired as e:
        if label:
            print(f"  [gh] {label}: {e}")
        return []


def fetch_pr_details(pr_number: int, github_repo: str) -> dict[str, Any] | None:
    args = [
        "pr",
        "view",
        str(pr_number),
        "--repo",
        github_repo,
        "--json",
        (
            "number,title,body,state,isDraft,author,headRefName,baseRefName,"
            "createdAt,updatedAt,closedAt,mergedAt,"
            "additions,deletions,changedFiles,"
            "commits,reviews,comments,labels,assignees,reviewRequests,url"
        ),
    ]
    return _gh_json(args, f"PR #{pr_number} details")


def fetch_pr_files(pr_number: int, github_repo: str) -> list[dict[str, Any]]:
    args = [
        "api",
        f"/repos/{github_repo}/pulls/{pr_number}/files",
        "--paginate",
        "--jq",
        ".[] | {path, patch, status, additions, deletions}",
    ]
    return _gh_lines(args, f"PR #{pr_number} files")


def fetch_pr_review_comments(pr_number: int, github_repo: str) -> list[dict[str, Any]]:
    args = [
        "api",
        f"/repos/{github_repo}/pulls/{pr_number}/comments",
        "--jq",
        ".[] | {id, user, body, path, line, position}",
    ]
    return _gh_lines(args, f"PR #{pr_number} review comments")


def search_prs_by_key(task_key: str, github_repo: str) -> list[dict[str, str]]:
    """Search GitHub PRs mentioning a Jira issue key. Fallback when dev-status API returns nothing."""
    import re

    prs: list[dict[str, str]] = []
    seen: set[str] = set()
    for state in ["open", "closed", "merged"]:
        args = [
            "search",
            "prs",
            f"{task_key} in:title,body",
            "--repo",
            github_repo,
            "--state",
            state,
            "--json",
            "number,title,url,state",
        ]
        results = _gh_json(args, f"search PRs for {task_key} ({state})")
        if not results:
            continue
        for pr in results:
            pr_url = (pr.get("url") or "").strip()
            if not pr_url or pr_url in seen:
                continue
            seen.add(pr_url)
            match = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", pr_url)
            if match:
                prs.append(
                    {
                        "repo": match.group(1),
                        "number": str(pr.get("number", "")),
                        "url": pr_url,
                        "title": pr.get("title", ""),
                        "state": pr.get("state", "UNKNOWN"),
                    }
                )
    return prs
