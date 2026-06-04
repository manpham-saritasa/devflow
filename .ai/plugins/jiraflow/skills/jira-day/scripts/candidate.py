from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from common import fmt_dt
from context import RuntimeContext


@dataclass
class Candidate:
    key: str
    summary: str
    status: str
    priority: str
    assignee: str
    evidence: set[str] = field(default_factory=set)
    last_activity: datetime | None = None
    logged_seconds: int = 0
    notes: list[str] = field(default_factory=list)

    def add_evidence(self, tag: str, when: datetime, note: str = "") -> None:
        self.evidence.add(tag)
        self.last_activity = (
            when if self.last_activity is None else max(self.last_activity, when)
        )
        if note:
            self.notes.append(note)

    def _review_statuses(self, runtime: RuntimeContext) -> set[str]:
        return set(runtime.stage_groups.get("review", []))

    def _qa_statuses(self, runtime: RuntimeContext) -> set[str]:
        return set(runtime.stage_groups.get("qa", []))

    def _bucket_dev(self, runtime: RuntimeContext) -> int:
        if runtime.check_pr and "pr" in self.evidence:
            return 0
        if "git" in self.evidence:
            return 1
        if "transition" in self.evidence or "comment" in self.evidence:
            return 2
        return 3

    def _bucket_qa(self, runtime: RuntimeContext) -> int:
        if self.status in self._qa_statuses(runtime) and (
            "transition" in self.evidence or "comment" in self.evidence
        ):
            return 0
        if "comment" in self.evidence or "transition" in self.evidence:
            return 1
        return 2

    def _bucket_tm(self, runtime: RuntimeContext) -> int:
        if (
            self.status in self._review_statuses(runtime)
            and "transition" in self.evidence
        ):
            return 0
        if "comment" in self.evidence:
            return 1
        if "transition" in self.evidence:
            return 2
        return 3

    def _bucket_pm(self, runtime: RuntimeContext) -> int:
        if (
            self.status in self._review_statuses(runtime)
            and "transition" in self.evidence
        ):
            return 0
        if "comment" in self.evidence:
            return 1
        if "transition" in self.evidence or "updated" in self.evidence:
            return 2
        return 3

    def _bucket_mixed(self) -> int:
        strong = {"pr", "git", "transition", "comment"}
        strong_count = len(self.evidence & strong)
        if strong_count >= 2:
            return 0
        if strong_count == 1:
            return 1
        return 2

    def bucket(self, runtime: RuntimeContext) -> int:
        if runtime.role == "dev":
            return self._bucket_dev(runtime)
        if runtime.role == "qa":
            return self._bucket_qa(runtime)
        if runtime.role == "tm":
            return self._bucket_tm(runtime)
        if runtime.role == "pm":
            return self._bucket_pm(runtime)
        return self._bucket_mixed()

    def logged_label(self) -> str:
        if self.logged_seconds <= 0:
            return "not logged"
        hours = self.logged_seconds // 3600
        minutes = (self.logged_seconds % 3600) // 60
        if hours and minutes:
            return f"{hours}h {minutes}m today"
        if hours:
            return f"{hours}h today"
        return f"{minutes}m today"

    def to_dict(self, runtime: RuntimeContext) -> dict[str, Any]:
        return {
            "key": self.key,
            "url": f"https://{runtime.jira_domain}.atlassian.net/browse/{self.key}",
            "summary": self.summary,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "evidence": sorted(self.evidence),
            "last_activity": fmt_dt(self.last_activity),
            "logged": self.logged_label(),
            "bucket": self.bucket(runtime),
            "notes": self.notes[:5],
        }
