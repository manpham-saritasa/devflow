---
name: dev-ship-pr-jira
description: ship feature to create GitHub PR and comment Jira task. Extract task ID from branch, generate report from changelog or git diff, push to develop, comment Jira.
triggers: 
  - "dev-ship-pr-jira"
  - "dev-ship-pr-jira --pr-only"
  - "dev-ship-pr-jira --jira-only"
  - "dev-ship-pr-jira --dry-run"
  - "dev-ship-pr-jira --technical-only"
  - "dev-ship-pr-jira --from-pr"
  - "dev-ship"
  - "dev-ship --pr-only"
  - "dev-ship --jira-only"
  - "dev-ship --dry-run"
  - "dev-ship --technical-only"
  - "dev-ship --from-pr"
  - "dev-ship --no-jira"
---

## When to Use

- `/dev-ship-pr-jira`, `/dev-ship` — create PR + comment Jira (default)
- `/dev-ship-pr-jira --pr-only`, `/dev-ship --pr-only` — create PR only, skip Jira
- `/dev-ship-pr-jira --jira-only`, `/dev-ship --jira-only` — comment Jira only, skip PR
- `/dev-ship-pr-jira --dry-run`, `/dev-ship --dry-run` — preview both changelogs, skip PR + Jira
- `/dev-ship-pr-jira --technical-only`, `/dev-ship --technical-only` — generate/preview technical changelog to `.local` only, skip PR + Jira
- `/dev-ship-pr-jira --from-pr [URL]`, `/dev-ship --from-pr [URL]` — generate reports from a past PR URL, skip PR + Jira (e.g. `https://github.com/owner/repo/pull/123`)
- `/dev-ship-pr-jira --no-jira`, `/dev-ship --no-jira` — create PR only, skip all Jira steps and Jira report. Use when repo has no Jira integration.
- `/dev-ship-pr-jira [KEY]`, `/dev-ship [KEY]` — explicit task key (auto-detected from branch if not given)

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Run all steps: PR + changelog + progress + Jira |
| `--pr-only` | Skip Step 8 (Jira comment) |
| `--jira-only` | Skip Step 6 (PR creation) |
| `--dry-run` | Skip Step 5b-9 (preview both changelogs). Show preview only. |
| `--technical-only` | Skip Step 6, 8 (PR, Jira). Generate changelog + progress to `.local` only. |
| `--from-pr [URL]` | Generate reports from a past GitHub PR. Skip Steps 5b-9 (no PR, no Jira). |
| `--no-jira` | Create PR + changelog + progress, skip Jira report and Jira comment. No `.env` file needed. |

## Paths

Read shared paths from `config.md`. `TASK_DIR` is defined there (as `[TASKS_ROOT]/[KEY]` where `TASKS_ROOT` = `.local/tasks`).

- `JIRA_TEMPLATE`: `jira-summary-template.md` — non-technical, for testers/PMs/clients
- `PR_TEMPLATE`: `pr-summary-template.md` — technical, for future engineers

## Jira Credentials

Read Jira credentials from `.env` in the repository root. Required variables:

```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_PROJECT_KEY=RMASUP
JIRA_EMAIL=john.doe@saritasa.com
JIRA_API_TOKEN=ATATT3xFfGF0eq6-JnkSzR-Example
```

- `JIRA_COMPANY_DOMAIN` — your Jira instance subdomain (the part before `.atlassian.net`)
- `JIRA_PROJECT_KEY` — the project key (e.g. `RMASUP`, `PROJ`)
- `JIRA_EMAIL` — the email associated with your Atlassian account
- `JIRA_API_TOKEN` — your Atlassian API token (generate at https://id.atlassian.com/manage-profile/security/api-tokens)

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

**Otherwise:** `git branch --show-current`, extract KEY regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY or Jira link. Stop if no valid KEY.

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

3. **Else:** `git diff develop..HEAD`, auto-extract + populate.

Rules for Jira report (skip if `--no-jira`):
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

Skip if `--from-pr` (no commit to build).

### Step 5: Show Preview and Write Changelog

Skip to Step 9 if `--dry-run` or `--from-pr` (read-only — show preview only, no writes).

Show the preview:

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

When `--from-pr`: omit the `Commit` and `Technical Changelog` lines — show only the PR and Jira reports.
When `--no-jira`: omit the `Jira Report` section. Show only the PR report.

### Step 5b: Write Technical Changelog

Skip if `--dry-run` or `--from-pr`.

Write/update `TASK_DIR/changelog.md` with the technical iteration (append new iteration, following the same iteration-number-as-heading format used by other skills). Create the file if it doesn't exist.

If `--technical-only`: after writing changelog, proceed to Step 7 (update progress), then skip to Step 9.

If NOT `--dry-run`, `--technical-only`, `--from-pr`: show both reports, ask "Ready? Say YES."

### Step 6: Create PR

Skip if `--jira-only`, `--dry-run`, `--technical-only`, or `--from-pr`:
```bash
git push origin $(git branch --show-current)
gh pr create --base develop --head $(git branch --show-current) --title "{MSG}" --body "{BODY}"
```
Capture PR URL. `{PR_BODY}` is the output from `PR_TEMPLATE`.

If `--no-jira`: the PR body uses only the PR report (no Jira report).

### Step 7: Update Progress

Skip if `--dry-run` or `--from-pr`:
- If `TASK_DIR/progress.md` exists: prepend status "Shipped", PR URL, timestamp
- Else: create new file

### Step 8: Comment Jira

Skip if `--pr-only`, `--dry-run`, `--technical-only`, `--from-pr`, or `--no-jira`.

Before commenting, verify `.env` is present in the repo root and contains all required variables (`JIRA_COMPANY_DOMAIN`, `JIRA_PROJECT_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`). If missing or incomplete, stop: "Jira credentials not found. Add them to `.env` in the repo root. See the Jira Credentials section for format."

Use Jira API with the credentials from `.env`:
- Base URL: `https://[JIRA_COMPANY_DOMAIN].atlassian.net`
- Auth: Basic auth using `[JIRA_EMAIL]:[JIRA_API_TOKEN]`
- Endpoint: `POST /rest/api/3/issue/[KEY]/comment`

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
          {
            "type": "text",
            "text": "{JIRA_BODY}\n\n"
          },
          {
            "type": "text",
            "text": "View PR: ",
            "marks": [{"type": "link", "attrs": {"href": "{PR_URL}"}}]
          }
        ]
      }
    ]
  }
}
```

**Required**: PR link must be a clickable markdown link at the BOTTOM of the comment body (format: `[View PR]({PR_URL})`). Never omit or move to top.
`{JIRA_BODY}` is the output from `JIRA_TEMPLATE`.

### Step 9: Success

```
✅ Changelog: .local/tasks/[KEY]/changelog.md
✅ PR: {PR_URL}
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/progress.md
```

If `--from-pr`:
```
✅ Reports generated from PR: {PR_URL}
```
If `--no-jira`:
```
✅ Changelog: .local/tasks/[KEY]/changelog.md
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/progress.md
```
If `--jira-only`:
```
✅ Changelog: .local/tasks/[KEY]/changelog.md
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/progress.md
```
If `--technical-only`:
```
✅ Changelog: .local/tasks/[KEY]/changelog.md
✅ Progress: .local/tasks/[KEY]/progress.md
```
(Omit skipped steps per flags.)
