# gmail-jira

Create a Jira task from a Gmail message + draft reply with task ID.

## User flow

```mermaid
flowchart TD
    A[User runs gmail-new] --> B[User picks email #N]
    B --> C[Step 2: Analyze email content]
    C --> D{Any field ambiguous?}
    D -->|Yes| E[Step 3: Ask open questions]
    E --> F[User answers]
    F --> C
    D -->|No| G[Step 4: Show proposal table]
    G --> H{User confirms?}
    H -->|Adjust| C
    H -->|Yes| I[Step 5: Create Jira task]
    I --> J[Step 6: Attach screenshots]
    J --> K[Step 7: Draft reply email]
    K --> L[Step 8: Report back]
    L --> M[Done]

    subgraph Jira Task
        I1[Set sprint]
        I2[Set component]
        I3[Set description from template]
        I --> I1 --> I2 --> I3
    end

    subgraph Filter Attachments
        J1[Skip image001.png]
        J2[LLM judges remaining]
        J3[Upload to Jira]
        J --> J1 --> J2 --> J3
    end
```

## Internal split

```mermaid
flowchart TD
    A[Gmail Message]:::accent0 --> B[gmail-jira]:::accent1

    B --> C[Fetch message]:::accent1
    B --> D[Clean body text]:::accent1
    B --> E[Classify attachments]:::accent1
    B --> F[Build reply draft]:::accent1

    B --> G[jira-create]:::accent2

    G --> H[Load Jira auth]:::accent2
    G --> I[Discover custom fields]:::accent2
    G --> J[Find active sprint]:::accent2
    G --> K[Build issue payload]:::accent2
    G --> L[Create Jira issue]:::accent2
    G --> M[Upload Jira attachments]:::accent2

    L --> N[Jira Issue Key]:::accent3
    F --> O[Gmail Draft]:::accent4
    M --> P[Attached Evidence]:::accent5

    N --> Q[Final result]:::accent6
    O --> Q
    P --> Q
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Full skill instructions (8 steps) |
| `templates/task-template.md` | Description template for Jira issues |
| `templates/reply-template.md` | Reply email body template |
| `scripts/main.py` | CLI entry point for proposal/create/draft flow |
| `scripts/*.py` | Gmail, Jira, ADF, and local config helpers |
| `README.md` | This file |

## Run

```bash
py.exe .ai/plugins/gmailflow/skills/gmail-jira/scripts/main.py --message-id 19e998921ffdd593 --project DEMOP --component "Field App"
py.exe .ai/plugins/gmailflow/skills/gmail-jira/scripts/main.py --message-id 19e998921ffdd593 --project DEMOP --component "Field App" --create --dry-run
py.exe .ai/plugins/gmailflow/skills/gmail-jira/scripts/main.py --message-id 19e998921ffdd593 --project DEMOP --component "Field App" --create
py.exe .ai/plugins/gmailflow/skills/gmail-jira/scripts/main.py --message-id 19e998921ffdd593 --project DEMOP --component "Field App" --create-draft --issue-key DEMOP-2197
```

## Dependencies

- **Gmail API** — `gmail.readonly` + `gmail.compose` scopes
- **Jira API** — REST v3 + Agile API
- `.env.gmail` — Google OAuth credentials
- `.env.jira` — Jira credentials
