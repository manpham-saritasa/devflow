---
name: release-list
description: List all tasks on develop not yet on main, grouped by task key with merged PR summaries, ordered newest first. Use for release preparation.
triggers:
  - "release-list"
  - "releaselist"
  - "release notes"
---

## When to Use

- Preparing a release — see what's on `develop` waiting to go to `main`
- Generating release notes from merged PRs
- Checking what tasks are pending release

## Workflow

### Step 1: Ensure on Develop

Check current branch:
```bash
git branch --show-current
```

If not on `develop`: "You are on `[branch]`. Switch to `develop` first? (yes / no)"
- If yes: `git checkout develop`
- If no: stop.

If `develop` branch does not exist: "No `develop` branch found in this repo." Stop.

### Step 2: Fetch and Pull Latest Develop

```bash
git fetch origin develop
git pull origin develop
```

If fetch or pull fails: "Failed to update `develop`. Check your network." Stop.

### Step 3: Get Commits on Develop Not on Main

```bash
git log main..develop --oneline --no-merges --format="%H %s"
```

If empty: "No new commits on `develop`. Nothing to release." Stop.

Extract task keys from commit messages using regex `([A-Z]+-\d+)`. Deduplicate. This gives the task list.

### Step 4: Find PRs for Each Task

For each unique task key, search for merged PRs:
```bash
gh search prs "[KEY]" --merged --json number,title,url,mergedAt,headRepository,headRepositoryOwner,baseRefName --limit 50
```

If `gh search prs` returns no results for a key, mark it as "no PR found" — still include it (may be a direct commit).

### Step 5: Sort by Newest

Sort tasks by the most recent PR merge date (descending). Tasks with no PR go to the bottom.

### Step 6: Present Release List

Format as a table. Each row = one task. Multiple PRs under one task are summarized.

```
## Release List — develop → main

| # | Task | PRs | Description |
|--|------|-----|-------------|
| 1 | [RMASUP-2145](https://saritasa.atlassian.net/browse/RMASUP-2145) | [#1435](url) | Adjust letter and word spacing in PDF exports |
| 2 | [RMASUP-2143](https://saritasa.atlassian.net/browse/RMASUP-2143) | 2 PRs: [#1430](url), [#1438](url) | Field App — new DR menu + pagination fix |
| 3 | [RMASUP-2134](https://saritasa.atlassian.net/browse/RMASUP-2134) | no PR found | Direct commit — GEO DB migration ADR |
```

Rules:
- Task key: clickable JIRA link (`https://[JIRA_COMPANY_DOMAIN].atlassian.net/browse/[KEY]`)
- PRs: clickable GitHub links. Single PR = `#[N]`. Multiple = `[N] PRs: #[A], #[B]`
- Description: from the first PR title (strip the task key and leading symbols)
- If no PR: use commit message summary

### Step 7: Show Summary

```
Total: [N] tasks pending release
PRs: [N] merged PRs
```

## JIRA URL

Build JIRA URLs using the domain from `.env` or `.env.local`:
```
JIRA_COMPANY_DOMAIN=saritasa
```
URL format: `https://[JIRA_COMPANY_DOMAIN].atlassian.net/browse/[KEY]`

If no JIRA domain found, use the task key as plain text (no link).

## Future Integration

The `jira-release` skill (in `jiraflow` plugin) will consume this list and add tasks to a JIRA release via:
```
jira-release --from-release-list --release-url https://saritasa.atlassian.net/projects/RMASUP/versions/123
```
