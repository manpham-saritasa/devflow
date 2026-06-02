---
name: jira-mine
description: List your assigned Jira tasks in pending states, ordered by priority within status groups.
triggers:
  - "jira-mine"
  - "jiramine"
  - "jmine"
  - "jira-task"
  - "jtask"
---

## Config

Read shared auth from `../../config.md`.

## Paths

- `CONFIG` — `./projects.config` (skill-relative)
- `IGNORE_FILE` — `./ignore-tasks.txt` (skill-relative) — one task key per line

---

## Workflow

Run the Python script and present its output cleanly in chat:

```bash
python .ai/plugins/jiraflow/jira-mine/scripts/main.py [--pending | --ready]
```

| Flag | Shows |
|------|-------|
| (none) | On-Going + Ready for Development |
| `--pending` | On-Going tasks only |
| `--ready` | Ready for Development tasks only |
| `--review` | Tasks needing your review (In Review, TM Review) |

Present the output as formatted markdown — not raw terminal output. Clean up any artifact spacing or separators. Use the script's actual data, not a template.

---

## Rules

| Rule | Detail |
|------|--------|
| Always re-query | Never reuse cached data. Each run must query Jira fresh. |
| Print to chat | Show the full script output in chat. Do not save to file. |
| Single project | Use `[PROJECT_KEY]` to switch. |
| Read-only | Never post comments or transition issues. |
