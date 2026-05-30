---
name: jira-move
description: Transition a Jira issue using milestone-based workflow. Per-project transition map + shared milestones config.
triggers:
  - "jira-move"
  - "jmove"
---

## Config

Read shared auth from ../../config.md. Milestones in ./milestones.config.

## Workflow

Run the Python script:

```bash
python .ai/plugins/jiraflow/jira-move/scripts/main.py KEY [MILESTONE] [--discover]
```

| Command | Action |
|---------|--------|
| `main.py KEY` | Auto-detect current milestone, advance to next |
| `main.py KEY ready` | Move to `ready` milestone (e.g., "Ready for Development") |
| `main.py KEY review` | Move to `review` milestone (e.g., "TM Review", "In Review") |
| `main.py KEY pending` | Move to `pending` milestone (e.g., "In Progress") |
| `main.py KEY verify` | Move to `verify` milestone (e.g., "On Staging", "On Production") |
| `main.py KEY complete` | Move to `complete` milestone (e.g., "Completed") |
| `main.py KEY --discover` | Explore all statuses, save transition map, restore task |

Accepts milestone names OR raw Jira status names.

---

## Config

**`milestones.config`** — shared across all projects:

```config
PIPELINE=backlog,ready,pending,code-review,ready-for-qa,in-qa,review,verify,complete

ready=Ready for Development,Ready to Do
pending=On Development,Doing,Do-ing,On going,In Progress
review=TM Review,In Review
verify=On Staging,On Production,Verified
complete=Completed,Completed.
```

**`PROJ.config`** — per-project transition map (auto-filled by --discover):

```config
Backlog=10=Blocked,221=Ready for Development,3=Completed
In Progress=10=Blocked,311=Code Review,351=Ready for Development
```
