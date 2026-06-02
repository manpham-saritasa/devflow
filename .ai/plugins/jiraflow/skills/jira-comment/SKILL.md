---
name: jira-comment
description: Post a comment to a Jira issue with an optional PR link at the bottom. Use when dev-ship needs to comment Jira, or any skill needs to notify a Jira task.
triggers:
  - "jira-comment"
  - "jcomment"
---

## Auth

Read from `.ai/plugins/jiraflow/config.md` Auth section. Required: `JIRA_COMPANY_DOMAIN`, `JIRA_PROJECT_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`.

## Usage

Called by other skills with `KEY`, `BODY`, and optional `PR_URL`:

```
jira-comment KEY "BODY TEXT" [PR_URL]
```

## Workflow

### Step 1: Verify Credentials

Check `.env` (then `.env.local`) for all required variables. Missing → stop.

### Step 2: Post Comment

```
POST https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/issue/[KEY]/comment
Authorization: Basic [base64(JIRA_EMAIL:JIRA_API_TOKEN)]
Content-Type: application/json

{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {"type": "text", "text": "{BODY}\n\n"},
          {"type": "text", "text": "View PR: ", "marks": [{"type": "link", "attrs": {"href": "{PR_URL}"}}]}
        ]
      }
    ]
  }
}
```

### Step 3: Rules

- PR link goes at the BOTTOM of the comment. Never at the top.
- Format: `[View PR]({PR_URL})` as a clickable markdown link.
- If no PR_URL, omit the link paragraph entirely.
- Body uses `JIRA_TEMPLATE` format: non-technical, behavior + user impact only.
