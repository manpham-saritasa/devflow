# jira-create

Create Jira issues with field discovery, sprint lookup, payload build, and attachment upload.

## Flow

```mermaid
flowchart TD
    A[Input proposal]:::accent0 --> B[jira-create]:::accent1

    B --> C[Load Jira auth]:::accent1
    B --> D[Load cached field IDs]:::accent1
    D --> E{Fields missing?}:::accent2
    E -->|yes| F[Discover via createmeta]:::accent2
    E -->|no| G[Use cache]:::accent3
    F --> H[Save cache]:::accent2

    B --> I[Find scrum board]:::accent4
    I --> J[Find active sprint]:::accent4

    G --> K[Build issue payload]:::accent5
    H --> K
    J --> K

    K --> L[Create Jira issue]:::accent6
    L --> M{Local files?}:::accent7
    M -->|yes| N[Upload attachments]:::accent7
    M -->|no| O[Done]:::accent3
    N --> O
```

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill instructions |
| `scripts/common.py` | Env load + Jira field cache |
| `scripts/jira_api.py` | Jira REST client |
| `scripts/create_flow.py` | Field discovery, sprint lookup, payload build, create/upload |
| `scripts/main.py` | CLI entry for proposal-based create |
| `README.md` | This file |

## Run

```bash
py.exe .ai/plugins/jiraflow/skills/jira-create/scripts/main.py --proposal proposal.json
```

## Notes

- Field cache path: `.local/gmailflow/jira-fields.json`
- Auth path: `.env.jira`
- Used by `gmail-jira` for Jira-side actions
