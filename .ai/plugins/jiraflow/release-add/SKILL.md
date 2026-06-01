---
name: release-add
description: Add one or more JIRA tasks to a JIRA release version. Provide task keys and release URL or name.
triggers:
  - "release-add"
  - "releaseadd"
  - "release-add"
---

## When to Use

- `release-add PROJ-2143 https://saritasa.atlassian.net/projects/PROJ/versions/123`
- `release-add PROJ-2143 "API next version"` — by release name
- `release-add PROJ-2143,PROJ-2145 https://...` — multiple tasks
- After reviewing `release-list` output, push selected tasks to a release

## Input

| Input | Format | Example |
|-------|--------|---------|
| Task key(s) | Comma-separated, no spaces | `PROJ-2143` or `PROJ-2143,PROJ-2145` |
| Release | Full JIRA release URL **or** release name | `https://saritasa.atlassian.net/.../versions/123` or `"API next version"` |

## Credentials

Read from `.env` or `.env.local` in repo root:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```

## Workflow

### Step 1: Parse Input

- Extract task keys from input (comma-separated, regex: `([A-Z]+-\d+)`)
- Extract release URL from input
- If no task keys: ask "Which tasks? (e.g. PROJ-2143)"
- If no release URL: ask "Release URL?"

### Step 2: Get Release Version ID

**If a JIRA release URL was provided:** extract the version ID from the URL.
Format: `https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID]`
The version ID is the last numeric path segment.

**If a release name was provided** (no URL, plain text like `"API next version"`):
search for the version by name:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/project/[JIRA_PROJECT_KEY]/version?query=[RELEASE_NAME]" \
  | jq -r '.values[0].id'
```

If multiple versions match, show them and ask which one.
If no version found: "No release named `[RELEASE_NAME]` found in project `[JIRA_PROJECT_KEY]`." Stop.

### Step 3: Get Task Summaries

For each task key, fetch the summary for confirmation:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/issue/[KEY]?fields=summary" \
  | jq -r '.fields.summary'
```

If any task key fails to resolve, show the error and ask whether to continue with the remaining tasks.

### Step 4: Confirm

Show what will be added:
```
Adding to release [VERSION_NAME]:
  1. PROJ-2143 — Field App: New DR menu
  2. PROJ-2145 — Adjust letter spacing

Proceed? (yes / no)
```

### Step 5: Add Tasks to Release

Use the JIRA issue update API to add `fixVersions`:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -X PUT \
  -H "Content-Type: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/issue/[KEY]" \
  -d '{"update":{"fixVersions":[{"add":{"id":"[VERSION_ID]"}}]}}'
```

Send one request per task. Status 204 = success.

If any task fails, show the error and continue with remaining tasks.

### Step 6: Report

```
✅ Added 2 task(s) to release [VERSION_NAME]:
   1. [PROJ-2143](https://saritasa.atlassian.net/browse/PROJ-2143)
   2. [PROJ-2145](https://saritasa.atlassian.net/browse/PROJ-2145)

Release: [RELEASE_URL or https://saritasa.atlassian.net/projects/PROJ/versions/ID]
```

Rules:
- Task key: clickable JIRA link
- Release: clickable URL to the release page
- If release was provided by name, build the URL from `https://[DOMAIN].atlassian.net/projects/[PROJECT_KEY]/versions/[ID]`

If any task failed to add, list them separately:
```
⚠️ Failed to add:
   - PROJ-2147: [error message]
```
