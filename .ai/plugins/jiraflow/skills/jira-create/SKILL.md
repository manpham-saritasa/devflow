---
name: jira-create
description: Create Jira issues with project metadata discovery, active sprint lookup, and optional attachment upload.
triggers:
  - "jira-create"
  - "create jira issue"
  - "jira issue create"
---

## Config

Read shared auth from `../../config.md`.

## Workflow

Run script for Jira-side create flow:

```bash
python .ai/plugins/jiraflow/skills/jira-create/scripts/main.py --proposal proposal.json
```

Use this skill for:
- Jira custom field discovery
- active sprint lookup
- issue payload build
- issue creation
- Jira attachment upload
