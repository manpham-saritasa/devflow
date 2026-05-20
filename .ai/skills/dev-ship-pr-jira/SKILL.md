---
name: dev-ship-pr-jira
description: |
  Ship feature: create GitHub PR, comment Jira task. Extract task ID from branch, generate report from changelog or git diff, push to develop, comment Jira.
  
triggers: 
  - "dev-ship-pr-jira"
  - "dev-ship-pr-jira --pr-only"
  - "dev-ship-pr-jira --jira-only"
  - "dev-ship-pr-jira --text-only"
  - "dev-ship-pr-jira --technical-only"
  - "dev-ship"
  - "dev-ship --pr-only"
  - "dev-ship --jira-only"
  - "dev-ship --text-only"
  - "dev-ship --technical-only"
---

## When to Use

- `/dev-ship-pr-jira`, `/dev-ship` — create PR + comment Jira (default)
- `/dev-ship-pr-jira --pr-only`, `/dev-ship --pr-only` — create PR only, skip Jira
- `/dev-ship-pr-jira --jira-only`, `/dev-ship --jira-only` — comment Jira only, skip PR
- `/dev-ship-pr-jira --text-only`, `/dev-ship --text-only` — preview both changelogs, skip PR + Jira
- `/dev-ship-pr-jira --technical-only`, `/dev-ship --technical-only` — generate/preview technical changelog to `.local` only, skip PR + Jira
- `/dev-ship-pr-jira [KEY]`, `/dev-ship [KEY]` — explicit task key (auto-detected from branch if not given)

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Run all steps: PR + progress + Jira |
| `--pr-only` | Skip Step 8 (Jira comment) |
| `--jira-only` | Skip Step 6 (PR creation) and Step 7 (progress update) |
| `--text-only` | Skip Step 6-9 (preview both changelogs). Show preview only. |
| `--technical-only` | Skip Step 6-9. Generate technical changelog to `.local` only. |

## Output Style

Use `REPORT_TEMPLATE`: `Added / Changed / Fixes` headings, numbered items [1][2][3], sub-bullets (Purpose/Details/Reason/Impact/Root cause/Resolution).
- Past tense, outcome-focused, minimal English
- **Never: variable names, function names, class names, file paths, method calls, code-level details. Behavior + user impact only. No exceptions.**
- Omit empty sections, bullet lists, short + scannable

## Paths

- DEV_ROOT: `.local`
- TASK_DIR: `.local/tasks/[KEY]`
- CHANGELOG_TEMPLATE: `.ai/agents/templates/changelog-template.md`
- PROGRESS_TEMPLATE: `.ai/agents/templates/progress-template.md`
- REPORT_TEMPLATE: `.ai/skills/dev-generate-report/report-template.md`

## Variables

- JIRA_DOMAIN: env var `$JIRA_DOMAIN`
- JIRA_PROJECT: env var `$JIRA_PROJECT`

## Workflow

### Step 1: Check Uncommitted Changes

`git status --short`. If uncommitted: list, ask "Commit or skip?"
- Commit: stop, wait for user, restart
- Skip: proceed

### Step 2: Extract Task ID

`git branch --show-current`, extract KEY regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY or Jira link. Stop if no valid KEY.

### Step 3: Extract Report Content

Generate report from branch evidence (commits, diff, changed files, Jira context).

Source priority:
1. If `TASK_DIR/changelog.md` exists: reclassify latest iteration into `Added / Changed / Fixes`, minimal English
2. Else: `git diff develop..HEAD`, auto-extract + populate

Rules:
- Jira = business intent; diff/commits/files = actual implementation
- If diff narrower than Jira, describe narrower shipped version
- Exclude refactors/renames/formatting/tests unless behavior changed
- Classification: Added = new capabilities | Changed = updated behavior | Fixes = bugs
- **Non-technical**: No variable/function/class/path/method/code-detail mentions. Behavior + user impact only. No exceptions.
- Short + specific main lines; past tense. Non-redundant sub-bullets only.
- Omit empty sections

### Step 4: Build Commit Message

Format: `{action} {description} [KEY]` (e.g., `Fix PDF landscape scaling [KEY]`)

### Step 5: Show Preview

If `--text-only`: show both changelogs, skip to Step 9.
If `--technical-only`: write/update `TASK_DIR/changelog.md` with technical iteration, show preview, skip to Step 9.

```
Commit: {MSG}

## Technical Changelog (.local)
## Iteration [N] — YYYY-MM-DD HH:MM ±TZ
### Summary
...
### Changes
...
### Fixes
...

## Non-Technical Report (Jira/GitHub)
## [KEY] — Title
## Added
[1] - ...
## Changed
[1] - ...
## Fixes
[1] - ...
```

If NOT `--text-only` or `--technical-only`: show report only, ask "Ready? Say YES."

### Step 6: Create PR

Skip if `--jira-only` or `--text-only`:
```bash
git push origin $(git branch --show-current)
gh pr create --base develop --head $(git branch --show-current) --title "{MSG}" --body "{BODY}"
```
Capture PR URL.

### Step 7: Update Progress

Skip if `--jira-only` or `--text-only`:
- If `TASK_DIR/progress.md` exists: prepend status "Shipped", PR URL, timestamp
- Else: create new file

### Step 8: Comment Jira

Skip if `--pr-only` or `--text-only`:
```
cloudId: [JIRA_DOMAIN]
issueIdOrKey: [KEY]
commentBody: {BODY}\n\n[View PR]({PR_URL})
contentFormat: markdown
```

**Required**: PR link must be a clickable markdown link at the BOTTOM of the comment body (format: `[View PR]({PR_URL})`). Never omit or move to top.

### Step 9: Success

```
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/progress.md
✅ Jira: [KEY] commented
```
(Omit skipped steps per flags.)
