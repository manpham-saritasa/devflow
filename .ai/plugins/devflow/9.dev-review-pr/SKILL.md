---
name: dev-review-pr
description: Review a GitHub PR across multiple quality dimensions. Supports current and past PRs. Provides structured feedback with prioritized issues and a downloadable report.
triggers:
  - "review-pr"
  - "reviewpr"
  - "dev-review-pr"
---

## When to Use

- `/review-pr [URL]` — review a specific PR (past or current)
- `/review-pr` or `/reviewpr` — auto-detect task key from worktree and find the open PR
- `/reviewpr [URL]` — shorthand with URL

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT` and `TASK_DIR` variables are defined there.

---

## Workflow

### Step 1: Detect PR

Parse input for a PR URL (regex: `github\.com/([^/]+)/([^/]+)/pull/(\d+)`).

**If a URL was provided:**
- Extract `OWNER`, `REPO`, and `PR_NUMBER` from the URL.
- Skip worktree detection — proceed directly to Step 2.

**If no URL was provided — auto-detect from worktree:**
```bash
git worktree list
```

If the current directory (`pwd`) appears in the output and the branch is not `main` or `develop`:
- `BRANCH_NAME` — the branch name in brackets
- Extract `KEY` via regex `([A-Z0-9]+-\d+)` from `BRANCH_NAME` (case-insensitive).
- Continue to PR lookup below.

**Legacy fallback — not in a worktree, on a regular branch:**
```bash
git branch --show-current
```

If the current branch is not `main` or `develop`, use it as `BRANCH_NAME` and extract `KEY`.

**If neither path yields a branch:** stop — "Not on a feature/hotfix branch and not in a worktree. Provide a PR URL or switch to your task branch first."

**Find the open PR for this branch:**
```bash
gh pr list --head "[BRANCH_NAME]" --state open --json number,title,url
```

| Result | Action |
|--------|--------|
| No open PR | "No open PR found for branch `[BRANCH_NAME]`." Stop. |
| Single PR | Save `PR_NUMBER`, `PR_URL`. Continue. |
| Multiple PRs | Show all and ask user to pick one. |

Extract `OWNER` and `REPO` from the PR URL.

### Step 2: Fail Fast — No PR

If no PR was found (no URL provided and no open PR detected), stop:
```
❌ No PR found. Provide a PR URL or ensure an open PR exists for the current branch.
Usage: /review-pr https://github.com/owner/repo/pull/123
```

### Step 3: Fetch Full PR Data

Fetch the PR metadata and all associated data in parallel:

```bash
# PR metadata
gh pr view [PR_NUMBER] --repo [OWNER]/[REPO] --json title,body,headRefName,baseRefName,state,mergeable,reviews,additions,deletions,files,commits

# PR diff
gh pr diff [PR_NUMBER] --repo [OWNER]/[REPO]
```

Parse the results:
- `PR_TITLE`, `PR_BODY`, `HEAD_BRANCH`, `BASE_BRANCH`, `PR_STATE`, `MERGEABLE`
- `REVIEWS[]` — each review's author, state (APPROVED/CHANGES_REQUESTED/COMMENTED), body
- `FILES[]` — each file's path, status (added/modified/deleted), additions, deletions
- `COMMITS[]` — each commit's message, oid, author
- `DIFF` — the full diff text

### Step 4: Extract Task Key

If `KEY` was already extracted from the branch name in Step 1, use it.

Otherwise, extract `KEY` from `PR_TITLE` or `HEAD_BRANCH` via regex `([A-Z0-9]+-\d+)` (case-insensitive).

If no `KEY` found: continue without it (the report will not be saved to a task folder, but the table review will still be shown).

### Step 5: Review Across Dimensions

Analyze the PR data (`FILES[]`, `DIFF`, `COMMITS[]`, `REVIEWS[]`, `PR_BODY`, `PR_TITLE`) across every dimension below. For each issue found, assign:

| Field | Description |
|-------|-------------|
| **Priority** | `Critical`, `High`, `Medium`, `Low` |
| **Review Category** | The dimension the issue falls under |
| **Checked File** | The file path where the issue was found |
| **Checked Line** | Line number(s) relevant to the issue |
| **Issue Summary** | Concise description of what is wrong |
| **Suggested Solution** | Actionable recommendation to fix it |

Priority definitions:
- `Critical` — security vulnerability, data loss, broken invariant, crash
- `High` — correctness bug, performance bottleneck, pattern violation, missing validation
- `Medium` — readability, naming, minor duplication, missing edge case
- `Low` — style preference, minor consistency, documentation, nitpick

#### 5a. Fit Check
- Does the PR title and description clearly explain what and why?
- Does the PR scope match what the branch name or task key suggests?
- Are changes scoped appropriately, or is there scope creep?
- Does `PR_BODY` reference necessary context (tickets, decisions, trade-offs)?
- Do commit messages follow the convention? (`{action} {description} #KEY`)
- Are the changes logically grouped into sensible commits?

#### 5b. Quality Check
- Readability: are variable/function/class names clear and self-documenting?
- Complexity: are there overly long functions, deep nesting, or convoluted logic?
- Duplication: is the same logic duplicated instead of reused?
- Magic values: are there hardcoded strings/numbers that should be constants?
- Comments: are complex sections explained, or are there noisy/stale comments?
- Error handling: are errors caught, logged, and handled gracefully?
- Boundary/edge cases: are null values, empty collections, and invalid inputs handled?

#### 5c. Naming Convention Check
- Do names follow the project's established conventions (casing, prefixes, suffixes)?
- Are abbreviations used consistently and meaningfully?
- Do test names describe the scenario and expected outcome?
- Do database migrations, config keys, and environment variables follow naming patterns?

#### 5d. Design Pattern Check
- Does the code follow established project patterns (repository, service, controller layers)?
- Are SOLID principles respected? (Single responsibility, Open/closed, etc.)
- Are abstractions appropriate, or is there over-engineering / under-engineering?
- Are new dependencies justified, or could existing ones be reused?
- Is the change consistent with the surrounding architecture?

#### 5e. Performance Check
- N+1 queries: are database queries made in loops?
- Repeated work: is the same computation done multiple times unnecessarily?
- Data volume: are large payloads fetched/processed when only a subset is needed?
- Caching: are expensive operations cached where appropriate?
- Resource cleanup: are streams, connections, and file handles properly disposed?

#### 5f. Security Check
- Input validation: is untrusted input validated, sanitized, or escaped?
- Injection: are raw inputs concatenated into SQL, HTML, shell commands, or URLs?
- Auth/authz: are protected endpoints/resources properly gated?
- Secrets: are credentials, tokens, or keys hardcoded or exposed in logs/output?
- Data exposure: is sensitive data (PII, tokens) returned in responses or logged?
- CSRF/XSS: are cross-site protections in place for web endpoints?

#### 5g. Testing Check
- Are new changes covered by tests?
- Do tests verify behavior, not implementation details?
- Are edge cases and error paths tested, or only the happy path?
- Are test names descriptive of the scenario?
- Are test assertions meaningful (not tautologies)?

#### 5h. Changelog / Documentation Check
- If a `changelog.md` exists in the task folder, does the diff match it?
- Are new public APIs, config options, or env vars documented?
- Are architectural decisions explained in the PR body or linked ADR?

### Step 6: Present Review Table

Display all findings as a table sorted by Priority (Critical → Low):

```
## PR Review — [PR_TITLE]

PR: [PR_URL]
Branch: [HEAD_BRANCH] → [BASE_BRANCH]
Files changed: [count] | +[additions] -[deletions] | [N] commits

| Priority | Review Category | Checked File | Checked Line | Issue Summary | Suggested Solution |
|----------|----------------|-------------|-------------|---------------|-------------------|
| Critical | Security | `src/login.php` | 42 | SQL injection via raw user input in query | Use parameterized query or ORM |
| High | Performance | `src/report.php` | 88-95 | N+1 query inside loop fetching user data | Eager-load users with JOIN |
| Medium | Naming Convention | `src/utils.php` | 12 | Abbreviation `calcAmt` instead of `calculateAmount` | Rename to `calculateAmount` |
| Low | Quality | `README.md` | 1 | Missing section for new env var | Add `NEW_FEATURE_FLAG` to env docs |
```

If no issues found:
```
✅ No issues found in this PR.

| Priority | Review Category | Checked File | Checked Line | Issue Summary | Suggested Solution |
|----------|----------------|-------------|-------------|---------------|-------------------|
| — | — | — | — | All checks passed | — |
```

### Step 7: Write Feedback Report

If `KEY` was extracted, write the report to `TASK_DIR/pr-feedback-[KEY].md`.

Ensure the `TASK_DIR` exists:
```bash
mkdir -p "[TASK_DIR]"
```

Report format:

```markdown
# PR Feedback — [KEY]

**PR:** [PR_TITLE]
**URL:** [PR_URL]
**Branch:** [HEAD_BRANCH] → [BASE_BRANCH]
**Reviewed:** YYYY-MM-DD HH:MM ±TZ

## Summary

- Files changed: [N] (+[additions] -[deletions])
- Commits: [N]
- Issues found: [N] (Critical: [N], High: [N], Medium: [N], Low: [N])

## Findings

| Priority | Review Category | Checked File | Checked Line | Issue Summary | Suggested Solution |
|----------|----------------|-------------|-------------|---------------|-------------------|
| ... | ... | ... | ... | ... | ... |

## Verdict

- **Changes requested** — one or more Critical or High priority issues found
- **Approved with suggestions** — only Medium/Low issues found
- **Approved** — no issues found

## Notes

[Any additional context, strengths observed, or recommendations for future work.]
```

If no `KEY` was found, display the report content in the chat instead and inform the user:
```
No task key detected. Report displayed above — save manually if needed.
```

### Step 8: Success Output

```
✅ Review complete for [PR_TITLE]

Issues found: [N] (Critical: [N], High: [N], Medium: [N], Low: [N])
Report: [TASK_DIR/pr-feedback-[KEY].md]

PR: [PR_URL]
```

---

## Self-Check

- [ ] PR detected from URL or auto-detected from worktree?
- [ ] Failed fast when no PR found?
- [ ] All PR data fetched (files, diff, commits, reviews)?
- [ ] Task key extracted when possible?
- [ ] All review dimensions checked?
- [ ] Issues assigned correct priority?
- [ ] Review table sorted by priority?
- [ ] Feedback report written to task folder (when key available)?
- [ ] Verdict reflects issue severity?
