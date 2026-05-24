---
name: dev-get-summary
description: Generate both non-technical (Jira) and technical (PR) changelog reports from task evidence. Preview reports without creating a PR or commenting Jira. Useful for past PRs, standalone reports, or dry-run previews.
triggers:
  - "dev-get-summary"
  - "get-summary"
  - "get-report"
---

## When to Use

- `/dev-get-summary [KEY]` — generate both reports from `.local/tasks/[KEY]/changelog.md`
- `/dev-get-summary` — auto-detect KEY from current branch, generate both reports
- `/dev-get-summary [PR_URL]` — generate both reports from a GitHub PR (e.g. `https://github.com/owner/repo/pull/123`)

Use this when:
- You want a clean report for a past PR, email, docs, or review
- You want to preview reports before shipping (dry-run)
- Another skill needs a non-technical or technical summary of changes
- You have a PR URL but no local changelog

## Paths

- DEV_ROOT: `.local`
- TASK_DIR: `[DEV_ROOT]/tasks/[KEY]` — replace `[KEY]` with Jira ticket key
- JIRA_TEMPLATE: `./jira-summary-template.md` — non-technical, for testers/PMs/clients
- PR_TEMPLATE: `./pr-summary-template.md` — technical, for future engineers

## Output Style

**Jira report** — use `JIRA_TEMPLATE`. Non-technical: behavior + user impact only. Audience: testers, PMs, clients. Never mention code-level details.

**PR report** — use `PR_TEMPLATE`. Technical: architecture, decisions, risks, reuse patterns. Audience: future engineers. Include file paths, method names, code patterns when relevant.

## Workflow

### Step 1: Extract Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY or Jira link. Stop if no valid KEY.

### Step 2: Read Source

Source priority (try each in order):

1. **PR URL provided** — If the user gives a GitHub PR URL, fetch it with `gh pr view [NUMBER] --repo [OWNER/REPO] --json ...` and `gh pr diff`. Extract the task key from the PR title or branch name. Use PR title, body, commits, reviews, files, and diff as evidence.

2. **Local changelog** — Read `TASK_DIR/changelog.md`. If it exists, use it.

3. **Git diff fallback** — Run `git diff develop..HEAD` to extract changes from the current branch.

If all sources are empty: stop and tell user "No evidence found for [KEY]. Provide a PR URL, create a changelog, or run from the feature branch."

### Step 3: Generate Both Reports

Generate TWO reports from the changelog evidence:

**Jira report** — follow `JIRA_TEMPLATE` strictly.
- Non-technical, business language.
- Added / Changed / Fixed / Testers / Notes sections.
- Omit empty sections.

**PR report** — follow `PR_TEMPLATE` strictly.
- Technical, engineering language.
- Goal / Added / Changed / Fixed / Key decisions / Risks / Testing / Related areas / Future reuse guidance sections.
- Omit empty sections.

### Step 4: Show Result

Display both reports as **separate copyable code blocks** so the user can copy each one independently:

**Jira Report:**
```
[rendered output from JIRA_TEMPLATE]
```

**PR Report:**
```
[rendered output from PR_TEMPLATE]
```

Rules:
- Always output two separate blocks with clear labels: `**Jira Report:**` and `**PR Report:**`.
- Each block must be a standalone fenced code block with no extra wrapping — the user should be able to triple-click and copy the entire report in one action.
- Do not merge both reports into a single block.
- Do not add extra commentary inside the code blocks.
