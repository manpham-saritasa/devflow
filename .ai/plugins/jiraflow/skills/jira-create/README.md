# jira-create

Create Jira issues with field discovery, sprint lookup, and payload build. Thin wrapper — all content decisions happen upstream.

## Architecture

Scripts process data, not generate content. 4-layer split:

```mermaid
flowchart TD
    subgraph Extract ["🔵 Extract — upstream skill"]
        A["gmail-jira parses email"]
    end

    subgraph Resolve ["🟠 Resolve — jira-create"]
        B["discover_fields()"] --> C["choose_scrum_board()"]
        C --> D["get_active_sprint()"]
    end

    subgraph Decide ["🟢 Decide — LLM"]
        E["generates summary, description, environment, estimate"]
    end

    subgraph Execute ["🔴 Execute — jira-create"]
        F["build_issue_fields()"] --> G["create_issue()"]
        G --> H["attach_file()"]
    end

    Extract --> Decide
    Resolve --> F
    Decide --> F
```

## Flow

```mermaid
flowchart TD
    A[Proposal JSON]:::accent0 --> B[load env + auth]:::accent1
    B --> C[load cached field IDs]:::accent1
    C --> D{Fields missing?}:::accent2
    D -->|yes| E[discover via createmeta API]:::accent2
    E --> F[save to .local/gmailflow/jira-fields.json]:::accent2
    D -->|no| G[use cache]:::accent3

    B --> H[find scrum board]:::accent4
    H --> I[find active sprint]:::accent4

    G --> J[build issue payload]:::accent5
    F --> J
    I --> J

    J --> K[POST /rest/api/3/issue]:::accent6
    K --> L[upload attachments]:::accent7
```

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill instructions |
| `scripts/main.py` | CLI entry — load proposal JSON, create issue |
| `../../shared/jira_api.py` | Jira REST client |
| `../../shared/create_flow.py` | Field discovery, sprint lookup, ADF, payload build |
| `../../shared/common.py` | Env loader + field cache |
| `README.md` | This file |

## Run

```bash
py.exe .ai/plugins/jiraflow/skills/jira-create/scripts/main.py --proposal proposal.json
```

## Dependencies

- `../../shared/` — shared jiraflow modules
- `.env.jira` — Jira credentials
- `.local/gmailflow/jira-fields.json` — cached custom field IDs

## Used by

- `gmail-jira` — passes LLM-generated proposal, jira-create handles Jira API
