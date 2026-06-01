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

### Step 2: Fetch Latest Develop and Main

```bash
git fetch origin develop
git fetch origin main
git pull origin develop
```

If fetch or pull fails: "Failed to update. Check your network." Stop.

Always use `origin/main` (not local `main`) — the local `main` branch may be stale.

### Step 3: Get PR Merge Commits on Develop Not on Main

```bash
git log --first-parent origin/main..develop --oneline --merges --format="%s" | grep 'Merge pull request'
```

If empty: "No new PR merges on `develop`. Nothing to release." Stop.

`--first-parent` follows only the linear history of `develop`, excluding side-branch merges (e.g. `main → develop` syncs) that would inflate the count.

Extract task keys from the branch name in each merge commit message using regex `(RMASUP-\d+)` (case-insensitive). Deduplicate. This gives the task list.

### Step 4: Find PR Details

Get all PR details in one batch:
```bash
gh pr list --repo [owner/repo] --search "is:merged sort:updated-desc" --limit 100 --json number,title,url,mergedAt
```

Cross-reference PR numbers from Step 3 with this data. If a PR number is not found in `gh pr list` output, fall back to individual lookup:
```bash
gh pr view [NUMBER] --json number,title,url,mergedAt
```

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
