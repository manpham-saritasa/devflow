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

## Paths

- DEV_ROOT: `.local`
- TASK_DIR: `[DEV_ROOT]/tasks/[KEY]` — replace [KEY] with Jira ticket key
- JIRA_TEMPLATE: `jira-summary-template.md` — non-technical, for testers/PMs/clients
- PR_TEMPLATE: `pr-summary-template.md` — technical, for future engineers

## Variables

- JIRA_DOMAIN: env var `$JIRA_DOMAIN`
- JIRA_PROJECT: env var `$JIRA_PROJECT`

## Output Style

**Jira comment** — use `JIRA_TEMPLATE`. Non-technical: behavior + user impact only. Audience: testers, PMs, clients. Never mention code-level details.

**PR body** — use `PR_TEMPLATE`. Technical: architecture, decisions, risks, reuse patterns. Audience: future engineers. Include file paths, method names, code patterns when relevant.

## Workflow

### Step 1: Check Uncommitted Changes

`git status --short`. If uncommitted: list, ask "Commit or skip?"
- Commit: stop, wait for user, restart
- Skip: proceed

### Step 2: Extract Task ID

`git branch --show-current`, extract KEY regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY or Jira link. Stop if no valid KEY.

### Step 3: Generate Reports

Generate TWO reports from branch evidence (commits, diff, changed files, Jira context):

**Jira report** — use `JIRA_TEMPLATE`. Non-technical, business language. Audience: testers/PMs/clients.
**PR report** — use `PR_TEMPLATE`. Technical, engineering language. Audience: future developers.

Source priority:
1. If `TASK_DIR/changelog.md` exists: reclassify latest iteration
2. Else: `git diff develop..HEAD`, auto-extract + populate

Rules for Jira report:
- Behavior + user impact only. No variable/function/class/path/method names.
- Past tense, outcome-focused. Short + scannable.
- Classification: Added = new capabilities | Changed = updated behavior | Fixed = bugs
- Omit empty sections.

Rules for PR report:
- Include file paths, method names, architectural decisions, code patterns.
- Group meaningful changes. Omit trivial refactors unless they support a key decision.
- Separate verified from not-verified in testing section.
- Mark reuse patterns with Safe to copy: YES/NO.

### Step 4: Build Commit Message

Format: `{action} {description} [KEY]` (e.g., `Fix PDF landscape scaling [KEY]`)

### Step 5: Show Preview

If `--text-only`: show both reports, skip to Step 9.
If `--technical-only`: write/update `TASK_DIR/changelog.md` with technical iteration, show preview, skip to Step 9.

```
Commit: {MSG}

## Technical Changelog (.local)
## Iteration [N] — YYYY-MM-DD HH:MM ±TZ
...

## PR Report (GitHub)
## [KEY] — Title
## Goal
...

## Jira Report
## [KEY] — Task summary
## Added
...
```

If NOT `--text-only` or `--technical-only`: show both reports, ask "Ready? Say YES."

### Step 6: Create PR

Skip if `--jira-only` or `--text-only`:
```bash
git push origin $(git branch --show-current)
gh pr create --base develop --head $(git branch --show-current) --title "{MSG}" --body "{BODY}"
```
Capture PR URL. `{PR_BODY}` is the output from `PR_TEMPLATE`.

### Step 7: Update Progress

Skip if `--jira-only` or `--text-only`:
- If `TASK_DIR/progress.md` exists: prepend status "Shipped", PR URL, timestamp
- Else: create new file

### Step 8: Comment Jira

Skip if `--pr-only` or `--text-only`:
```
cloudId: [JIRA_DOMAIN]
issueIdOrKey: [KEY]
commentBody: {JIRA_BODY}\n\n[View PR]({PR_URL})
contentFormat: markdown
```

**Required**: PR link must be a clickable markdown link at the BOTTOM of the comment body (format: `[View PR]({PR_URL})`). Never omit or move to top.
`{JIRA_BODY}` is the output from `JIRA_TEMPLATE`.

### Step 9: Success

```
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/progress.md
✅ Jira: [KEY] commented
```
(Omit skipped steps per flags.)
