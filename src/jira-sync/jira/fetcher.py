"""Raw markdown and task.json rendering for JiraTask objects."""

from pathlib import Path
from typing import Any

from dto.jira_task import JiraTask

_BUILTIN_TEMPLATE = """\
# {key} \u2014 {summary}

- **Status:** {status}
- **Type:** {issuetype}
- **Priority:** {priority}
- **Estimated:** {estimated}
- **Spent:** {spent}
- **Assignee:** {assignee}
- **Reporter:** {reporter}
- **Components:** {components}
- **Labels:** {labels}
- **Tags:** {tags}
- **Fix Versions:** {fix_versions}
- **Created:** {created}
- **Updated:** {updated}
- **Due Date:** {due_date}
- **Resolution:** {resolution}
- **Resolved At:** {resolution_date}
- **URL:** {url}

---

## Hierarchy

- **Epic:** {epic}
- **Sprint:** {sprint}
- **Parent:** {parent}
- **Story Points:** {story_points}
- **Subtasks:**{subtasks}

---

## Related Tasks

{related_tasks}

---

## Attachments

{attachments}

---

## Description

{description}

---

## Comments

{comments}
"""


def _load_template(template_paths: list[Path] | None = None) -> str:
    if template_paths:
        for path in template_paths:
            if path.exists():
                return path.read_text(encoding="utf-8")
    return _BUILTIN_TEMPLATE


def render_raw_md(
    task: JiraTask,
    jira_url: str = "",
    tags_field_id: str = "",
    template_paths: list[Path] | None = None,
) -> str:
    """Render JiraTask as a comprehensive raw.md markdown string."""
    template = _load_template(template_paths)

    description_text = task.description_text or ""
    description = (
        f"```\n{description_text}\n```" if description_text else "_(no description)_"
    )

    comments_md = "_(no comments)_"
    if task.comments:
        lines = []
        for c in task.comments:
            body = c.body_text[:500] if c.body_text else "_(empty comment)_"
            lines.append(f"**{c.author}** ({c.created}):\n\n```\n{body}\n```")
        comments_md = "\n\n---\n\n".join(lines)

    return (
        template.replace("{key}", task.key)
        .replace("{summary}", task.summary)
        .replace("{status}", task.status)
        .replace("{issuetype}", task.issuetype)
        .replace("{priority}", task.priority)
        .replace("{estimated}", task.estimated_str())
        .replace("{spent}", task.spent_str())
        .replace("{assignee}", task.assignee)
        .replace("{reporter}", task.reporter)
        .replace("{components}", task.component_str)
        .replace("{labels}", task.label_str)
        .replace("{tags}", task.tags_md(jira_url, tags_field_id))
        .replace("{fix_versions}", task.fix_version_str)
        .replace("{created}", task.created)
        .replace("{updated}", task.updated)
        .replace("{due_date}", task.due_date)
        .replace("{resolution}", task.resolution)
        .replace("{resolution_date}", task.resolution_date)
        .replace("{url}", JiraTask.browse_url(jira_url, task.key))
        .replace("{epic}", task.epic_md(jira_url))
        .replace("{sprint}", task.sprint_md())
        .replace("{parent}", task.parent_md(jira_url))
        .replace("{story_points}", task.story_points or "None")
        .replace("{subtasks}", task.subtasks_md(jira_url))
        .replace("{related_tasks}", task.related_tasks_md(jira_url))
        .replace("{attachments}", task.attachments_md())
        .replace("{description}", description)
        .replace("{comments}", comments_md)
    )


def build_task_json(
    task: JiraTask, download_path_rel: str, jira_url: str = ""
) -> dict[str, Any]:
    """Build structured task.json record from a JiraTask."""
    return task.to_json_record(download_path_rel, jira_url)
