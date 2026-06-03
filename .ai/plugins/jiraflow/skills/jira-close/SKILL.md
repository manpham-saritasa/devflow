---
name: jira-close
version: 0.1.0
description: Close Jira tasks by key, list, milestone, or release URL. Moves each to the complete milestone via jira-move.
triggers:
  - "jira-close"
  - "jiraclose"
  - "jclose"
  - "close release"
---

## Usage

| Input | Example |
|-------|---------|
| Single task | `jclose RMASUP-2164` |
| Multiple tasks | `jclose RMASUP-2164 RMASUP-2165 RMASUP-2166` |
| Milestone | `jclose RMASUP review` |
| Release URL | `jclose https://saritasa.atlassian.net/projects/RMASUP/versions/54192` |

## Workflow

### Step 1: Parse Input

- **If URL**: extract version ID. Go to Step 2a.
- **If milestone name** (e.g. `review`, `verify`): go to Step 2c.
- **If task key(s)**: go to Step 2b.

### Step 2a: From Release URL

Fetch all tasks in the release:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/search/jql?jql=fixVersion%3D[VERSION_ID]&fields=status&maxResults=200"
```

Show summary, ask confirmation, then close.

### Step 2b: From Task Key(s)

Show each task with current status, ask confirmation, then close.

### Step 2c: From Milestone

Resolve milestone to Jira statuses using `milestones.config` (shared with jira-move):

```
PIPELINE=backlog,ready,in-progress,code-review,ready-for-qa,in-qa,review,verify,complete
review=TM Review,In Review
verify=On Staging,On Production,Verified
```

Fetch all tasks in matching statuses:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/search/jql?jql=project%3D[PROJECT_KEY]+AND+status+in+(%22TM%20Review%22%2C%22In%20Review%22)&fields=status&maxResults=200"
```

Show summary:
```
⚠️ [N] tasks in milestone "review" — [PROJECT_KEY]

| # | Task | Status |
|---|------|--------|
| 1 | [KEY](url) | TM Review |
...

Close all [N] tasks? (yes/no)
```

### Step 3: Move Each Task to Complete

For each task, delegate to jira-move:

```bash
python .ai/plugins/jiraflow/skills/jira-move/scripts/main.py [KEY] complete
```

If jira-move fails (missing transitions), use direct API to discover and apply transitions:

```bash
# Step 1: Get available transitions
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/issue/[KEY]/transitions"

# Step 2: Apply transition by ID
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"transition": {"id": "[ID]"}}' \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/issue/[KEY]/transitions"
```

Re-fetch transitions after each step — the Complete option may require multiple hops.

### Step 4: Report

```
## Closed — [N] tasks

| # | Task | Result |
|---|------|--------|
| 1 | [KEY](url) | ✅ Completed |
| 2 | [KEY](url) | ✅ Completed |
| 3 | [KEY](url) | ⏭️ Already complete |

Release: [NAME](URL)  (if from release URL)
Milestone: [MILESTONE] (if from milestone)
```

## Credentials

Read from `.env` or `.env.local`:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```

## Milestones

Uses the same `milestones.config` as jira-move. Resolves milestone names to Jira statuses.

## Rules

| Rule | Detail |
|------|--------|
| Always confirm | Show task list before closing |
| Delegate transitions | Use jira-move for each task |
| Skip already complete | Don't error on tasks already done |
| Show context | Include release URL or milestone in final output |
