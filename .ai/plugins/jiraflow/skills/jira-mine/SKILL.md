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
python .ai/plugins/jiraflow/skills/jira-mine/scripts/main.py [--pending | --ready]
```

| Flag | Shows |
|------|-------|
| (none) | On-Going + Ready for Development |
| `--pending` | On-Going tasks only |
| `--ready` | Ready for Development tasks only |
| `--review` | Tasks needing your review (In Review, TM Review) |

### Output rules

- Read the raw output from the Python script using `terminal` tool.
- Present the output as formatted markdown — not raw terminal output.
- Every task must be shown with a **clickable URL**: `[PROJ-123](https://<domain>.atlassian.net/browse/PROJ-123)`.
- Do not paraphrase or summarize task descriptions — show the actual text from the script.
- Never save to file — print directly in chat.

---

## Rules

| Rule | Detail |
|------|--------|
| Always re-query | Never reuse cached data. Each run must query Jira fresh. |
| Print to chat | Show the full script output in chat. Do not save to file. |
| Single project | Use `[PROJECT_KEY]` to switch. |
| Read-only | Never post comments or transition issues. |
