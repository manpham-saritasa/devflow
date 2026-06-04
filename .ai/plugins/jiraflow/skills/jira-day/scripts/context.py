from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RuntimeContext:
    project: str
    role: str
    check_pr: bool
    stage_groups: dict[str, list[str]]
    window_hours: int
    jira_domain: str
    prefer_projects: list[str]


@dataclass(frozen=True)
class EvidenceContext:
    account_id: str
    cutoff: datetime
    domain: str
    auth: str
    git_map: dict[str, datetime]
    pr_map: dict[str, datetime]
