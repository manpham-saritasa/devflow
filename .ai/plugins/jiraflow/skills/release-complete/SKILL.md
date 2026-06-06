---
name: release-complete
version: 0.1.0
description: Finalize a JIRA release — close all tasks and mark as Released with today's date. Auto-runs jira-close if needed.
triggers:
  - "release-complete"
  - "releasecomplete"
  - "rcomplete"
  - "complete release"
---

## Workflow

### Step 1: Parse Release URL

Extract version ID from input: `https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID]`.

### Step 2: Get Release Info + Tasks

Fetch release name:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/version/[VERSION_ID]"
```

Fetch all tasks in the release:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/search/jql?jql=fixVersion%3D[VERSION_ID]&fields=status&maxResults=200"
```

### Step 3: Check Task Statuses

Count tasks by status. If any task is NOT in the complete milestone (e.g. not "Completed", "Done"):

```
⚠️ [N] tasks not yet completed:

| # | Task | Status |
|---|------|--------|
| 1 | [KEY-1](url) | In Progress |
...

Close all [N] tasks first? (yes/no)
```

If user says yes: run `jira-close` for this release.
If all tasks already complete: skip to Step 5.

### Step 4: Close Remaining Tasks

Delegate to jira-close:

Follow the jira-close workflow: fetch tasks, confirm, move each to complete via jira-move.

### Step 5: Mark as Released

```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"released": true, "releaseDate": "[YYYY-MM-DD]"}' \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/version/[VERSION_ID]"
```

Use today's date in `YYYY-MM-DD` format.

### Step 6: Report

```
✅ Release finalized
   [VERSION_NAME](https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID])
   Date: [YYYY-MM-DD]
   Tasks: [N] closed, [S] already complete
```

## Credentials

Read from `.env` or `.env.jira`:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```

## Rules

| Rule | Detail |
|------|--------|
| Auto-close | If tasks aren't complete, offer to run jira-close |
| Always confirm | Show release name + task summary before marking Released |
| Use today's date | `releaseDate` = current date in YYYY-MM-DD |
| Show release URL | Always include clickable link in final output |
