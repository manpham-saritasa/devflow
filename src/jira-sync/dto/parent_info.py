from dataclasses import dataclass


@dataclass
class ParentInfo:
    key: str
    summary: str
    status: str
    issue_type: str | None
    url: str
