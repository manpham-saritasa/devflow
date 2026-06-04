from datetime import datetime, timedelta, timezone
from typing import Any

from candidate import Candidate
from common import (
    NOISY_UPDATE_FIELDS,
    extract_task_keys,
    extract_text,
    now_utc,
    parse_gh_dt,
    parse_jira_dt,
    run_command,
)
from context import EvidenceContext, RuntimeContext
from jira_client import fetch_account, fetch_changelog, fetch_issues
from settings import jira_auth
from worklogs import get_today_worklogs


def collect_git_activity(root: str, hours: int) -> dict[str, datetime]:
    out: dict[str, datetime] = {}
    since = f"{hours} hours ago"
    log_out = run_command(
        ["git", "--no-pager", "log", f"--since={since}", "--pretty=%cI\t%s\t%b"], root
    )
    for line in log_out.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        try:
            dt = datetime.fromisoformat(parts[0].replace("Z", "+00:00")).astimezone(
                timezone.utc
            )
        except Exception:
            dt = now_utc()
        for key in extract_task_keys(" ".join(parts[1:])):
            out[key] = max(out.get(key, dt), dt)
    branch = run_command(["git", "branch", "--show-current"], root)
    if branch:
        ts = now_utc()
        for key in extract_task_keys(branch):
            out[key] = max(out.get(key, ts), ts)
    return out


def pr_queries(cutoff: str) -> list[list[str]]:
    return [
        [
            "gh",
            "search",
            "prs",
            f"--updated={cutoff}",
            "--author=@me",
            "--json",
            "title,body,updatedAt,headRefName,url",
        ],
        [
            "gh",
            "search",
            "prs",
            f"--updated={cutoff}",
            "--reviewed-by=@me",
            "--json",
            "title,body,updatedAt,headRefName,url",
        ],
        [
            "gh",
            "search",
            "prs",
            f"--updated={cutoff}",
            "--commenter=@me",
            "--json",
            "title,body,updatedAt,headRefName,url",
        ],
    ]


def merge_pr_items(out: dict[str, datetime], items: list[dict[str, Any]]) -> None:
    for item in items:
        joined = " ".join(
            [item.get("title", ""), item.get("body", ""), item.get("headRefName", "")]
        )
        try:
            updated_at = parse_gh_dt(item.get("updatedAt"))
        except Exception:
            updated_at = now_utc()
        for key in extract_task_keys(joined):
            out[key] = max(out.get(key, updated_at), updated_at)


def collect_pr_activity(root: str, hours: int, enabled: bool) -> dict[str, datetime]:
    if not enabled:
        return {}
    cutoff = (now_utc() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out: dict[str, datetime] = {}
    for cmd in pr_queries(cutoff):
        text = run_command(cmd, root)
        if not text:
            continue
        try:
            items = __import__("json").loads(text)
        except Exception:
            continue
        merge_pr_items(out, items)
    return out


def apply_comment_evidence(
    candidate: Candidate,
    comments: list[dict[str, Any]],
    account_id: str,
    cutoff: datetime,
) -> None:
    for comment in comments:
        if comment.get("author", {}).get("accountId") != account_id:
            continue
        created = parse_jira_dt(comment["created"])
        if created < cutoff:
            continue
        candidate.add_evidence(
            "comment", created, extract_text(comment.get("body", ""))[:120]
        )


def apply_changelog_evidence(
    candidate: Candidate,
    changelog: list[dict[str, Any]],
    account_id: str,
    cutoff: datetime,
) -> None:
    for hist in changelog:
        if (hist.get("author") or {}).get("accountId") != account_id:
            continue
        created = parse_jira_dt(hist["created"])
        if created < cutoff:
            continue
        meaningful_update_fields: list[str] = []
        for item in hist.get("items", []):
            field_name = str(item.get("field") or "")
            field_key = field_name.strip().lower()
            if field_key == "status":
                candidate.add_evidence(
                    "transition",
                    created,
                    f"{item.get('fromString', '?')} -> {item.get('toString', '?')}",
                )
                continue
            if field_key in NOISY_UPDATE_FIELDS:
                continue
            meaningful_update_fields.append(field_name)
        if meaningful_update_fields:
            candidate.add_evidence(
                "updated", created, f"updated {', '.join(meaningful_update_fields[:3])}"
            )


def make_candidate(issue: dict[str, Any]) -> Candidate:
    fields = issue["fields"]
    return Candidate(
        issue["key"],
        fields.get("summary", "?"),
        fields.get("status", {}).get("name", "?"),
        fields.get("priority", {}).get("name", "?"),
        (fields.get("assignee") or {}).get("displayName", "Unassigned"),
    )


def build_candidate_maps(
    root: str, hours: int, check_pr: bool
) -> tuple[dict[str, int], dict[str, datetime], dict[str, datetime]]:
    return (
        get_today_worklogs(root),
        collect_git_activity(root, hours),
        collect_pr_activity(root, hours, check_pr),
    )


def apply_issue_evidence(
    candidate: Candidate,
    issue: dict[str, Any],
    evidence: EvidenceContext,
    local_logged_seconds: int,
) -> None:
    key = issue["key"]
    if key in evidence.git_map:
        candidate.add_evidence("git", evidence.git_map[key], "git activity")
    if key in evidence.pr_map:
        candidate.add_evidence("pr", evidence.pr_map[key], "PR activity")
    fields = issue["fields"]
    apply_comment_evidence(
        candidate,
        fields.get("comment", {}).get("comments", []),
        evidence.account_id,
        evidence.cutoff,
    )
    apply_changelog_evidence(
        candidate,
        fetch_changelog(evidence.domain, evidence.auth, key),
        evidence.account_id,
        evidence.cutoff,
    )
    candidate.logged_seconds = max(candidate.logged_seconds, local_logged_seconds)


def filter_candidates(
    candidates: dict[str, Candidate], config: dict[str, Any]
) -> dict[str, Candidate]:
    exclude_statuses = set(config.get("exclude_statuses") or [])
    exclude_projects = set(config.get("exclude_projects") or [])
    return {
        key: item
        for key, item in candidates.items()
        if key.split("-", 1)[0] not in exclude_projects
        and item.status not in exclude_statuses
        and item.evidence
    }


def collect_candidates(
    root: str,
    env: dict[str, str],
    config: dict[str, Any],
    runtime: RuntimeContext,
) -> dict[str, Candidate]:
    domain, _, auth = jira_auth(env, config)
    account_id = fetch_account(domain, auth)["accountId"]
    cutoff = now_utc() - timedelta(hours=runtime.window_hours)
    issues = fetch_issues(domain, auth, runtime.project, runtime.window_hours)
    worklogs, git_map, pr_map = build_candidate_maps(
        root, runtime.window_hours, runtime.check_pr
    )
    evidence = EvidenceContext(
        account_id=account_id,
        cutoff=cutoff,
        domain=domain,
        auth=auth,
        git_map=git_map,
        pr_map=pr_map,
    )
    candidates: dict[str, Candidate] = {}

    for issue in issues:
        key = issue["key"]
        candidate = candidates.setdefault(key, make_candidate(issue))
        apply_issue_evidence(candidate, issue, evidence, worklogs.get(key, 0))

    return filter_candidates(candidates, config)
