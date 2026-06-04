from typing import Any

from candidate import Candidate
from context import RuntimeContext


def rank_candidates(
    candidates: dict[str, Candidate],
    runtime: RuntimeContext,
) -> list[Candidate]:
    project_rank = {key: i for i, key in enumerate(runtime.prefer_projects or [])}

    def sort_key(item: Candidate) -> tuple[Any, ...]:
        project = item.key.split("-", 1)[0]
        recent = item.last_activity.timestamp() if item.last_activity else 0
        return (
            item.bucket(runtime),
            project_rank.get(project, 999),
            1 if item.logged_seconds > 0 else 0,
            -recent,
            -len(item.evidence),
            item.key,
        )

    return sorted(candidates.values(), key=sort_key)


def build_output(
    items: list[Candidate],
    runtime: RuntimeContext,
) -> str:
    lines = [f"jira-day — last {runtime.window_hours}h", ""]
    if not items:
        return "\n".join(lines + ["No candidate tasks found."])
    lines += ["Suggested: #1", ""]
    for index, item in enumerate(items, 1):
        data = item.to_dict(runtime)
        lines.append(f"{index}. {data['key']}")
        lines.append(f"   url: {data['url']}")
        lines.append(f"   evidence: [{', '.join(data['evidence'])}]")
        lines.append(f"   last activity: {data['last_activity']}")
        lines.append(f"   logged: {data['logged']}")
        lines.append(f"   summary: {data['summary']}")
        lines.append(
            f"   status: {data['status']} | priority: {data['priority']} | assignee: {data['assignee']}"
        )
        if data["notes"]:
            lines.append(f"   notes: {data['notes'][0]}")
        lines.append("")
    return "\n".join(lines).rstrip()
