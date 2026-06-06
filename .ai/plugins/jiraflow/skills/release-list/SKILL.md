---
name: release-list
version: 0.1.0
description: List releases in a Jira project. Shows release name and URL. Optionally filter by released, unreleased, or all.
triggers:
  - "release-list"
  - "releaselist"
  - "rlist"
  - "list releases"
---

## Usage

- `jira-list RMASUP` — list open releases
- `jira-list RMASUP --released` — list released versions
- `jira-list RMASUP --all` — list all versions

## Workflow

### Step 1: Parse Input

Extract project key from first argument: `RMASUP`.
Default to `JIRA_PROJECT_KEY` from `.env.jira` if no key provided.

### Step 2: Fetch Versions

| Flag | API filter |
|------|-----------|
| (none) | `status=unreleased` |
| `--released` | `status=released` |
| `--all` | no filter |

```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/project/[PROJECT_KEY]/version?[FILTER]&orderBy=-startDate&maxResults=50"
```

### Step 3: Format Output

Show as a table with clickable links:

```
## [PROJECT_KEY] — [N] releases

| # | Name | URL |
|---|------|-----|
| 1 | LIMS next version | https://.../versions/52594 |
| 2 | API next version | https://.../versions/54092 |
```

If empty: "No releases found for `[PROJECT_KEY]`."

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
| Default project | Use `JIRA_PROJECT_KEY` from `.env.jira` if no key provided |
| Show URLs | Always include clickable release URLs |
