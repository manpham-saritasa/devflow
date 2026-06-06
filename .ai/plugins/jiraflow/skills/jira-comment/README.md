# jira-comment

Post a comment to a Jira issue with an optional PR link.

## 1. Quick start

```bash
jira-comment PROJ-123 "Reviewed and approved. Ready for QA."
jira-comment PROJ-123 "Fix deployed." https://github.com/owner/repo/pull/42
```

## 2. Output

```text
✅ Comment posted to PROJ-123
```

## 3. Setup

Same `.env.jira` as other jiraflow skills. No additional config needed.

## 4. Flow

```mermaid
flowchart TD
    A[Parse KEY, BODY, PR_URL] --> B[Load auth from .env.jira]
    B --> C[Jira auth OK?]
    C -->|no| D[Stop: missing credentials]
    C -->|yes| E[Build comment body in ADF format]
    E --> F{PR_URL given?}
    F -->|yes| G[Append PR link to body]
    F -->|no| H[Post as-is]
    G --> H
    H --> I[POST /rest/api/3/issue/KEY/comment]
    I --> J[Output success]
```

### External calls

| Source | Call type |
|---|---|
| Jira REST API | HTTP POST comment |

## 5. File structure

```text
skills/jira-comment/
  SKILL.md    ← skill description + workflow
  README.md   ← this file
```
