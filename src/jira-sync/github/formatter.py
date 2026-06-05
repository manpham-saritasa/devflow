"""PR formatter for GitHub PR data. Delegates helpers to GithubUtils."""

from typing import Any

from github.github_utils import GithubUtils


class PRFormatter:
    """Formats GitHub PR data into a markdown string."""

    @staticmethod
    def _login(user: dict[str, Any] | None) -> str:
        return GithubUtils.login(user)

    @staticmethod
    def _yn(value: bool | None) -> str:
        return GithubUtils.yes_no(value)

    @staticmethod
    def _dt(value: str | None, fallback: str = "n/a") -> str:
        return GithubUtils.date_or(value, fallback)

    @staticmethod
    def _should_skip_file(filepath: str | None) -> bool:
        return GithubUtils.should_skip_file(filepath)

    @staticmethod
    def _load_pr_template() -> str:
        return GithubUtils.load_pr_template()

    def format_files_bullets(self, files: list[dict[str, Any]]) -> str:
        source = [f for f in files if not self._should_skip_file(f.get("path") or "")]
        return GithubUtils.format_bullets(
            source,
            lambda f: (
                f"- `{f.get('path', '?')}` ({f.get('status', '?')})"
                f" +{f.get('additions', 0)} / -{f.get('deletions', 0)}"
            ),
        )

    def format_commits_bullets(self, commits: list[dict[str, Any]]) -> str:
        return GithubUtils.format_bullets(
            commits,
            lambda c: (
                f"- `{(c.get('oid') or '')[:7]}`"
                f" — {c.get('messageHeadline') or c.get('message') or '(no message)'}"
            ),
        )

    def format_reviews_bullets(self, reviews: list[dict[str, Any]]) -> str:
        return GithubUtils.format_bullets(reviews, lambda r: self._fmt_review(r))

    def _fmt_review(self, r: dict[str, Any]) -> str:
        login = self._login(r.get("author"))
        state = r.get("state", "COMMENTED")
        body = (r.get("body") or "").split("\n")[0][:200]
        if state == "APPROVED":
            return f"- **@{login}:** {state}"
        if body:
            return f"- **@{login}:** {state} — {body}"
        return f"- **@{login}:** {state}"

    def format_issue_comments_bullets(self, comments: list[dict[str, Any]]) -> str:
        return GithubUtils.format_bullets(
            comments,
            lambda c: (
                f"- **@{self._login(c.get('author'))}**"
                f" ({(c.get('createdAt') or '')[:10]}):"
                f" {(c.get('body') or '').split(chr(10))[0][:200]}"
            ),
        )

    def format_review_comments_bullets(
        self, review_comments: list[dict[str, Any]]
    ) -> str:
        return GithubUtils.format_bullets(
            review_comments,
            lambda c: (
                f"- **@{self._login(c.get('user'))}**"
                f" (`{c.get('path') or '?'}`:"
                f"{c.get('line') or c.get('position') or '?'}):"
                f" {(c.get('body') or '').split(chr(10))[0]}"
            ),
        )

    def format_labels_bullets(self, labels: list[dict[str, Any]]) -> str:
        return GithubUtils.format_bullets(
            labels,
            lambda lab: f"- {lab.get('name') or '?'}",
        )

    def format_reviewers_bullets(
        self, review_requests: list[dict[str, Any]], assignees: list[dict[str, Any]]
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
        return "\n".join(lines) if lines else GithubUtils.none_marker()

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
