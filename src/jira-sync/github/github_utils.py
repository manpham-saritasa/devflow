"""Static utility methods for GitHub PR formatting."""

import re
from typing import Any, Callable

from jira.config import PR_TEMPLATE_PATH

_NONE = "_(none)_"

_SKIP_FILE_PATTERNS = [
    re.compile(r"^\.claude/"),
    re.compile(r"^docs/ai-knowledge/"),
    re.compile(r"\.md$"),
    re.compile(r"^\.gitignore$"),
]


class GithubUtils:
    """Namespace for GitHub-related static helpers."""

    @staticmethod
    def login(user: dict[str, Any] | None) -> str:
        if not user:
            return "unknown"
        return user.get("login") or "unknown"

    @staticmethod
    def yes_no(value: bool | None) -> str:
        return "Yes" if value else "No"

    @staticmethod
    def date_or(value: str | None, fallback: str = "n/a") -> str:
        return value or fallback

    @staticmethod
    def should_skip_file(filepath: str | None) -> bool:
        if not filepath:
            return True
        for pat in _SKIP_FILE_PATTERNS:
            if pat.search(filepath):
                return True
        return False

    @staticmethod
    def load_pr_template() -> str:
        if PR_TEMPLATE_PATH.exists():
            return PR_TEMPLATE_PATH.read_text(encoding="utf-8")
        return _BUILTIN_PR_TEMPLATE

    @staticmethod
    def format_bullets(
        items: list[dict[str, Any]],
        formatter: Callable[[dict[str, Any]], str],
    ) -> str:
        if not items:
            return _NONE
        return "\n".join(formatter(i) for i in items)

    @staticmethod
    def none_marker() -> str:
        return _NONE


_BUILTIN_PR_TEMPLATE = """\
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
