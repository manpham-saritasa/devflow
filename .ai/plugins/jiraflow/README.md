# Jiraflow Plugin

JIRA workflow skills for release management.

## Structure

```
jiraflow/
  release-add/                ← add task(s) to a JIRA release version
  release-note/               ← generate client-friendly release notes
```

## Skills

| # | Skill | Benefits | Example |
|---|-------|----------|---------|
| 1 | `release-add` | Add task to JIRA release version via API | `release-add PROJ-2143 "API next version"` |
| 2 | `release-note` | Generate client-facing release note from JIRA | `release-note "API next version"` |

## Future

- `release-create` — create a new release version in JIRA
- `release-status` — show progress of a release
