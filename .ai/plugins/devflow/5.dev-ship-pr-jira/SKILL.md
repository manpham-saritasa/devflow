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

### Step 4: Build Commit Message

Format: `{action} {description} KEY` (e.g., `Fix PDF landscape scaling KEY`)

Skip if `--from-pr` (no commit to build).

### Step 5: Show Preview

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

If `--dry-run` or `--from-pr`: skip to Step 9 (read-only — no PR, no Jira, no writes).

If `--technical-only`: proceed to Step 7 (update progress), then skip to Step 9.

If NOT `--dry-run`, `--technical-only`, `--from-pr`: ask "Ready? Say YES."

### Step 6: Create or Reuse PR

Skip if `--jira-only`, `--dry-run`, `--technical-only`, or `--from-pr`.

Before creating a PR, check whether an open PR already exists for the current branch.

```bash
gh pr list --state open --json number,title,url,headRefName,baseRefName
```

Filter by `headRefName == $(git branch --show-current)`.

- If an open PR already exists for this branch: **fail fast for PR creation**. Do **not** create another PR.
- Reuse the existing PR URL.
- Generate a short comment that summarizes changes from the recent commits since the PR branch was last updated.
- Post that summary to the existing PR with `gh pr comment [PR_NUMBER] --body "[SUMMARY]"`.
- Continue to Step 7 using the existing PR URL.

If no open PR exists for the current branch:
```bash
git push origin $(git branch --show-current)
gh pr create --base [BASE_BRANCH] --head $(git branch --show-current) --title "{MSG}" --body "{BODY}"
```

`[BASE_BRANCH]` must match the repository default branch (for example `main` or `develop`). Do not assume `develop` if the repository uses another default branch.

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

If a new PR was created:
```
✅ PR: {PR_URL}
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/progress.md
```

If an existing PR was reused:
```
✅ PR reused: {PR_URL}
✅ PR comment added with recent changes summary
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/progress.md
```

If `--from-pr`:
```
✅ Reports generated from PR: {PR_URL}
```
If `--no-jira` and a new PR was created:
```
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/progress.md
```
If `--no-jira` and an existing PR was reused:
```
✅ PR reused: {PR_URL}
✅ PR comment added with recent changes summary
✅ Progress: .local/tasks/[KEY]/progress.md
```
If `--jira-only`:
```
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/progress.md
```
If `--technical-only`:
```
✅ Progress: .local/tasks/[KEY]/progress.md
```
(Omit skipped steps per flags.)
