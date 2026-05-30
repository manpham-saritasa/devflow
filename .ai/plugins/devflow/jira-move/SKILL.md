---
name: jira-move
description: Transition a Jira issue to a target status using per-project config with full transition map.
triggers:
  - "jira-move"
  - "jmove"
---

## Workflow

Run the Python script:

```bash
python .ai/plugins/devflow/jira-move/main.py KEY [ready|review|qa|in-progress] [--discover]
```

| Command | Action |
|---------|--------|
| `main.py KEY` | Auto-detect current status, move to next step |
| `main.py KEY ready` | Move to Ready For Development |
| `main.py KEY review` | Move to Code Review |
| `main.py KEY qa` | Move to Ready For QA |
| `main.py KEY in-progress` | Move to In Progress |
| `main.py KEY --discover` | Explore all statuses + transitions, save to config, restore task |

---

## Config Format

```config
PIPELINE=Backlog, Ready for Development, In Progress, Code Review, Ready for QA

Backlog=10=Blocked,221=Ready for Development,3=Completed
Ready for Development=10=Blocked,231=In Progress,241=Backlog
```

- `PIPELINE` — ordered dev flow, used for auto-detection and --discover probing
- `STATUS=ID=TO,ID=TO` — full transition map for each visited status

New project: copy `PROJECT-KEY.config.template` → `PROJ.config`, edit pipeline, run `--discover`.
