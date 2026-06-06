# gmail-jira

Create a Jira task from a Gmail message + draft reply with task ID.

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

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Full skill instructions (8 steps) |
| `templates/task-template.md` | Description template for Jira issues |
| `templates/reply-template.md` | Reply email body template |
| `README.md` | This file |

## Dependencies

- **Gmail API** — `gmail.readonly` + `gmail.compose` scopes
- **Jira API** — REST v3 + Agile API
- `.env.gmail` — Google OAuth credentials
- `.env.jira` — Jira credentials
