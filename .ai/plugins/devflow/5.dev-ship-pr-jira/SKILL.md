---
name: dev-ship-pr-jira
version: 0.1.0
description: ship feature to create GitHub PR and comment Jira task. Extract task ID from branch, generate report from changelog or git diff, push to develop, comment Jira.
triggers:
  - "dev-ship"
  - "devship"
  - "dev-ship-pr-jira"
---

## When to Use

- `/dev-ship-pr-jira`, `/dev-ship` — create PR + comment Jira (default)
- `/dev-ship-pr-jira --pr-only`, `/dev-ship --pr-only` — create PR only, skip Jira
- `/dev-ship-pr-jira --jira-only`, `/dev-ship --jira-only` — comment Jira only, skip PR
- `/dev-ship-pr-jira --dry-run`, `/dev-ship --dry-run` — preview both reports, skip PR + Jira
- `/dev-ship-pr-jira --technical-only`, `/dev-ship --technical-only` — preview technical report + write progress to `.local` only, skip PR + Jira
- `/dev-ship-pr-jira --from-pr [URL]`, `/dev-ship --from-pr [URL]` — generate reports from a past PR URL, skip PR + Jira (e.g. `https://github.com/owner/repo/pull/123`)
- `/dev-ship-pr-jira --no-jira`, `/dev-ship --no-jira` — create PR only, skip all Jira steps and Jira report. Use when repo has no Jira integration.
- `/dev-ship-pr-jira [KEY]`, `/dev-ship [KEY]` — explicit task key (auto-detected from branch if not given)

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Run all steps: PR + progress + Jira |
| `--pr-only` | Skip Step 8 (Jira comment) |
| `--jira-only` | Skip Step 6 (PR creation) |
| `--dry-run` | Show preview only. Skip Steps 6-8 (no PR, no Jira, no writes). |
| `--technical-only` | Skip Steps 6, 8 (PR, Jira). Show preview + write progress to `.local` only. |
| `--from-pr [URL]` | Generate reports from a past GitHub PR. Skip Steps 5-9 (no PR, no Jira, no writes). |
| `--no-jira` | Create PR + progress, skip Jira report and Jira comment. No `.env` file needed. |

## Paths

Read shared paths from `config.md`.
## Output Style

**Jira comment** — use `JIRA_TEMPLATE`. Non-technical: behavior + user impact only. Audience: testers, PMs, clients. Never mention code-level details.

**PR body** — use `PR_TEMPLATE`. Technical: architecture, decisions, risks, reuse patterns. Audience: future engineers. Include file paths, method names, code patterns when relevant.

## Workflow

### Step 1: Check Uncommitted Changes

Skip if `--from-pr`.

`git status --short`. If uncommitted: list, ask "Commit or skip?"
- Commit: stop, wait for user, restart
- Skip: proceed

### Step 2: Extract Task ID

**If `--from-pr [URL]`:** parse `OWNER`, `REPO`, and `PR_NUMBER` from the URL. Fetch the PR and extract KEY from the title or branch name:
```bash
gh pr view [PR_NUMBER] --repo [OWNER]/[REPO] --json title,headRefName
```
Extract KEY via regex `([A-Z0-9]+-\d+)` from `title` or `headRefName`. If fail: ask user for KEY. Stop if no valid KEY.

Otherwise: `git branch --show-current`, extract KEY regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY or Jira link. Stop if no valid KEY.

**Ensure feature branch:** Check if on `main` or `develop`. If so, call `dev-start [KEY]` first, then restart. Skip this check if using --jira-only, --from-pr, --dry-run, or --technical-only.

### Step 3: Generate Reports

If `--no-jira`: generate only the **PR report** (technical). Skip the Jira report entirely.

Otherwise, generate TWO reports:

**Jira report** — use `JIRA_TEMPLATE`. Non-technical, business language. Audience: testers/PMs/clients.
**PR report** — use `PR_TEMPLATE`. Technical, engineering language. Audience: future developers.

Source priority:
1. **If `--from-pr [URL]`:** fetch PR details and diff as evidence:
   ```bash
   gh pr view [PR_NUMBER] --repo [OWNER]/[REPO] --json title,body,commits,reviews,files
   gh pr diff [PR_NUMBER] --repo [OWNER]/[REPO]
   ```
   Use PR title, body, commits, reviews, files, and diff. Skip local changelog and git diff.

2. **If `TASK_DIR/changelog.md` exists:** reclassify latest iteration.

3. **Else:** `git diff [BASE_BRANCH]..HEAD  # main if no develop`, auto-extract + populate.

Rules for Jira report (skip if `--no-jira`):
- Behavior + user impact only. No variable/function/class/path/method names.
- Past tense, outcome-focused. Short + scannable.
- Classification: Added = new capabilities | Changed = updated behavior | Fixed = bugs
- Omit empty sections.

Rules for PR report:
- Include file paths, method names, architectural decisions, code patterns.
- Group meaningful changes. Omit trivial refactors unless they support a key decision.
- Separate verified from not-verified in testing section.

### Step 4: Build Commit Message

Format: `{action} {description} KEY` (e.g., `Fix PDF landscape scaling KEY`)

Skip if `--from-pr` (no commit to build).

### Step 5: Show Preview

Show the preview in separate copyable blocks.

```text
Commit: {MSG}
```

```md
## Technical Changelog (.local)
## Iteration [N] — YYYY-MM-DD HH:MM ±TZ
...
```

```md
## PR Report (GitHub)
## [KEY] — Title
## Goal
...
```

```md
## Jira Report
## [KEY] — Task summary
## Added
...
```

When `--from-pr`: omit the `Commit` and `Technical Changelog` blocks — show only the PR and Jira blocks.
When `--no-jira`: omit the `Jira Report` block. Show only the PR block.
Each block should stay separate so the user can copy the PR body or Jira comment directly.

If `--dry-run` or `--from-pr`: skip to Step 9 (read-only — no PR, no Jira, no writes).

If `--technical-only`: proceed to Step 7 (update progress), then skip to Step 9.

If NOT `--dry-run`, `--technical-only`, `--from-pr`: ask "Proceed? (yes / no)"

### Step 6: Create or Reuse PR

Skip if `--jira-only`, `--dry-run`, `--technical-only`, or `--from-pr`.

Call `create-pr` skill with `KEY`, `MSG`, and `PR_BODY`. Capture `PR_URL`. See `.ai/plugins/githubflow/create-pr/SKILL.md`.

### Step 7: Update Progress in Plan

Skip if `--dry-run` or `--from-pr`:
- If `TASK_DIR/plan.md` exists: append progress row with status "Shipped", PR URL, timestamp
- Else: skip progress update

### Step 8: Comment Jira

Skip if `--pr-only`, `--dry-run`, `--technical-only`, `--from-pr`, or `--no-jira`.

Call `jira-comment` skill with `KEY`, `JIRA_BODY` (from JIRA_TEMPLATE), and `PR_URL`. See `.ai/plugins/jiraflow/jira-comment/SKILL.md`.

### Step 9: Success

Use `templates/success-output.md` — pick the block matching the flags used. Omit skipped blocks.

### Step 10: Update Jira Status

Call `jira-move` skill with `KEY` and milestone `code-review`. Non-blocking — continue on failure.
