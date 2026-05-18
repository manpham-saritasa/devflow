"""PR formatting utilities for GitHub PR data."""

import re
from typing import Any

from config import PR_TEMPLATE_PATH

_SKIP_FILE_PATTERNS = [
    re.compile(r"^\.claude/"),
    re.compile(r"^docs/ai-knowledge/"),
    re.compile(r"\.md$"),
    re.compile(r"^\.gitignore$"),
]


class PRFormatter:
    """Formats GitHub PR data into a markdown string."""

    @staticmethod
    def _login(user: dict[str, Any] | None) -> str:
        if not user:
            return "unknown"
        return user.get("login") or "unknown"

    @staticmethod
    def _yn(value: bool | None) -> str:
        return "Yes" if value else "No"

    @staticmethod
    def _dt(value: str | None, fallback: str = "n/a") -> str:
        return value or fallback

    @staticmethod
    def _should_skip_file(filepath: str | None) -> bool:
        if not filepath:
            return True
        for pat in _SKIP_FILE_PATTERNS:
            if pat.search(filepath):
                return True
        return False

    @staticmethod
    def _load_pr_template() -> str:
        if PR_TEMPLATE_PATH.exists():
            return PR_TEMPLATE_PATH.read_text(encoding="utf-8")
        # fallback built-in template
        return """\
# PR #{{ number }} — {{ title }}

- **Repository:** {{ repository_or_unknown }}
- **Task:** {{ task_key }}
- **State:** {{ state }}
- **Draft:** {{ draft_yes_no }}
- **Merged:** {{ merged_yes_no }}
- **Author:** {{ author_or_unknown }}
- **Base Branch:** {{ base_ref_or_unknown }}
- **Head Branch:** {{ head_ref_or_unknown }}
- **Created:** {{ created_at_or_unknown }}
- **Updated:** {{ updated_at_or_unknown }}
- **Closed:** {{ closed_at_or_not_closed }}
- **Merged At:** {{ merged_at_or_not_merged }}
- **URL:** {{ url_or_unknown }}

## Summary

{{ body_or_no_description }}

## Stats

- **Commits:** {{ stats.commits }}
- **Issue Comments:** {{ stats.comments }}
- **Review Comments:** {{ stats.review_comments }}
- **Additions:** {{ stats.additions }}
- **Deletions:** {{ stats.deletions }}
- **Changed Files:** {{ stats.changed_files }}

## Labels

{{ labels_bullets }}

## Reviewers

{{ reviewers_and_assignees_bullets }}

## Changed Files

{{ files_bullets }}

## Commits

{{ commits_bullets }}

## Reviews

{{ reviews_bullets }}

## Issue Comments

{{ issue_comments_bullets }}

## Review Comments

{{ review_comments_bullets }}
"""

    def format_files_bullets(self, files: list[dict[str, Any]]) -> str:
        source = [f for f in files if not self._should_skip_file(f.get("path") or "")]
        if not source:
            return "_(none)_"
        lines: list[str] = []
        for f in source:
            path = f.get("path", "?")
            status = f.get("status", "?")
            add_n = f.get("additions", 0)
            del_n = f.get("deletions", 0)
            lines.append(f"- `{path}` ({status}) +{add_n} / -{del_n}")
        return "\n".join(lines)

    def format_commits_bullets(self, commits: list[dict[str, Any]]) -> str:
        if not commits:
            return "_(none)_"
        lines: list[str] = []
        for c in commits:
            oid = (c.get("oid") or "")[:7]
            msg = c.get("messageHeadline") or c.get("message") or "(no message)"
            lines.append(f"- `{oid}` — {msg}")
        return "\n".join(lines)

    def format_reviews_bullets(self, reviews: list[dict[str, Any]]) -> str:
        if not reviews:
            return "_(none)_"
        lines: list[str] = []
        for r in reviews:
            login = self._login(r.get("author"))
            state = r.get("state", "COMMENTED")
            body = (r.get("body") or "").split("\n")[0][:200]
            if state == "APPROVED":
                lines.append(f"- **@{login}:** {state}")
            elif body:
                lines.append(f"- **@{login}:** {state} — {body}")
            else:
                lines.append(f"- **@{login}:** {state}")
        return "\n".join(lines)

    def format_issue_comments_bullets(self, comments: list[dict[str, Any]]) -> str:
        if not comments:
            return "_(none)_"
        lines: list[str] = []
        for c in comments:
            login = self._login(c.get("author"))
            created = (c.get("createdAt") or "")[:10]
            body = (c.get("body") or "").split("\n")[0][:200]
            lines.append(f"- **@{login}** ({created}): {body}")
        return "\n".join(lines)

    def format_review_comments_bullets(
        self,
        review_comments: list[dict[str, Any]],
    ) -> str:
        if not review_comments:
            return "_(none)_"
        lines: list[str] = []
        for c in review_comments:
            login = self._login(c.get("user"))
            path = c.get("path") or "?"
            line_num = c.get("line") or c.get("position") or "?"
            body = (c.get("body") or "").split("\n")[0]
            lines.append(f"- **@{login}** (`{path}`:{line_num}): {body}")
        return "\n".join(lines)

    def format_labels_bullets(self, labels: list[dict[str, Any]]) -> str:
        if not labels:
            return "_(none)_"
        lines: list[str] = []
        for lab in labels:
            name = lab.get("name") or "?"
            lines.append(f"- {name}")
        return "\n".join(lines)

    def format_reviewers_bullets(
        self,
        review_requests: list[dict[str, Any]],
        assignees: list[dict[str, Any]],
    ) -> str:
        lines: list[str] = []
        if review_requests:
            for rr in review_requests:
                login = self._login(rr.get("requestedReviewer"))
                if login != "unknown":
                    lines.append(f"- @{login} (reviewer)")
        if assignees:
            for a in assignees:
                login = self._login(a)
                if login != "unknown":
                    lines.append(f"- @{login} (assignee)")
        return "\n".join(lines) if lines else "_(none)_"

    def render(
        self,
        pr_details: dict[str, Any],
        files: list[dict[str, Any]],
        review_comments: list[dict[str, Any]],
        task_key: str,
        github_repo: str,
    ) -> str:
        template = self._load_pr_template()

        commits = pr_details.get("commits") or []
        comments = pr_details.get("comments") or []
        reviews = pr_details.get("reviews") or []
        labels = pr_details.get("labels") or []
        assignees = pr_details.get("assignees") or []
        review_requests = pr_details.get("reviewRequests") or []

        merged_at = pr_details.get("mergedAt")
        closed_at = pr_details.get("closedAt")

        return (
            template.replace("{{ number }}", str(pr_details.get("number", "?")))
            .replace("{{ title }}", pr_details.get("title") or "(no title)")
            .replace("{{ repository_or_unknown }}", github_repo or "unknown")
            .replace("{{ task_key }}", task_key)
            .replace("{{ state }}", (pr_details.get("state") or "unknown").upper())
            .replace("{{ draft_yes_no }}", self._yn(pr_details.get("isDraft")))
            .replace("{{ merged_yes_no }}", self._yn(bool(merged_at)))
            .replace("{{ author_or_unknown }}", self._login(pr_details.get("author")))
            .replace(
                "{{ base_ref_or_unknown }}", pr_details.get("baseRefName") or "unknown"
            )
            .replace(
                "{{ head_ref_or_unknown }}", pr_details.get("headRefName") or "unknown"
            )
            .replace(
                "{{ created_at_or_unknown }}", self._dt(pr_details.get("createdAt"))
            )
            .replace(
                "{{ updated_at_or_unknown }}", self._dt(pr_details.get("updatedAt"))
            )
            .replace("{{ closed_at_or_not_closed }}", self._dt(closed_at, "Not closed"))
            .replace("{{ merged_at_or_not_merged }}", self._dt(merged_at, "Not merged"))
            .replace("{{ url_or_unknown }}", pr_details.get("url") or "unknown")
            .replace(
                "{{ body_or_no_description }}",
                pr_details.get("body") or "_(No description provided)_",
            )
            .replace("{{ stats.commits }}", str(len(commits)))
            .replace("{{ stats.comments }}", str(len(comments)))
            .replace("{{ stats.review_comments }}", str(len(review_comments)))
            .replace("{{ stats.additions }}", str(pr_details.get("additions", 0)))
            .replace("{{ stats.deletions }}", str(pr_details.get("deletions", 0)))
            .replace(
                "{{ stats.changed_files }}",
                str(pr_details.get("changedFiles", len(files))),
            )
            .replace("{{ labels_bullets }}", self.format_labels_bullets(labels))
            .replace(
                "{{ reviewers_and_assignees_bullets }}",
                self.format_reviewers_bullets(review_requests, assignees),
            )
            .replace("{{ files_bullets }}", self.format_files_bullets(files))
            .replace("{{ commits_bullets }}", self.format_commits_bullets(commits))
            .replace("{{ reviews_bullets }}", self.format_reviews_bullets(reviews))
            .replace(
                "{{ issue_comments_bullets }}",
                self.format_issue_comments_bullets(comments),
            )
            .replace(
                "{{ review_comments_bullets }}",
                self.format_review_comments_bullets(review_comments),
            )
        )
