# Prompts Index

| Name | Summary | Usage / Note |
|---|---|---|
| `get-changelog.md` | Generates concise, user-facing changelog content from branch evidence (diffs, commits, Jira context) formatted for Jira or GitHub PR comments. | Run against the current local branch after implementation is complete. Output uses Added / Changed / Fixes sections with numbered, outcome-focused bullets. |
| `get-jira-task.md` | Transforms a single Jira issue into an implementation-ready task specification in Markdown, incorporating context from related historical issues. | Designed as a Rovo prompt for use inside Jira. Produces a structured `task.md` with Overview, Requirements, Acceptance Criteria, Constraints, Affected Modules, Related Historical Tasks, Open Questions, and Technical Notes. |
| `review-change-one-by-one.md` | Shows each planned change as a scrollable option list, confirms individually, executes all at once. | Use when reviewing planned changes — never execute before final confirmation. |
