---
name: dev-review-pr
description: Review a GitHub PR across key quality checks. Supports current and past PRs. Outputs prioritized findings and a saved report.
triggers:
  - "review-pr"
  - "reviewpr"
  - "dev-review-pr"
---

## When to Use

- `/review-pr [URL]` — review a specific PR (past or current)
- `/review-pr` or `/reviewpr` — auto-detect task key from worktree and find the open PR
- `/reviewpr [URL]` — shorthand with URL
- `/review-pr --code-base` or `/reviewpr --code-base` — also check the local codebase. Fail fast if not on the correct worktree/branch.

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Fetch and review from PR data only (files, diff, commits, reviews) |
| `--code-base` | Also check local task context, project conventions, and related source files. Fail if HEAD branch does not exist locally. |

## Paths

Read shared paths from `config.md`.

---

## Workflow

### Step 1: Detect PR

Parse input for a PR URL (regex: `github\.com/([^/]+)/([^/]+)/pull/(\d+)`).
Parse flags: `--code-base`.

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

Fetch core PR data. If any result looks truncated, note that in the review:

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

### Step 3a: Check Codebase (if `--code-base`)

Skip this step if `--code-base` flag is not set.

**Fail fast — verify local branch context:**
- Check that `[HEAD_BRANCH]` exists locally.
- Prefer running from the matching worktree or branch.
- If the branch is missing locally: stop — "The `[HEAD_BRANCH]` branch does not exist locally. Switch to the correct worktree first."

**Fetch codebase context:**

Task context:
- Read `.local/tasks/[KEY]/task.md` if it exists.
- Read `.local/tasks/[KEY]/plan.md` if it exists.
- If task files are missing, note that and continue.

Project conventions:
- Inspect common project config files if present, for example lint, format, type-check, or style config.
- Note which config files were found.

Related files:
- For each changed file in `FILES[]`, inspect nearby files in the same directory when useful.
- Use this only to understand local patterns, naming, and architecture.

Store as `TASK_CONTEXT`, `PROJECT_CONFIGS`, and `RELATED_FILES[]`.

### Step 4: Extract Task Key

If `KEY` was already extracted from the branch name in Step 1, use it.

Otherwise, extract `KEY` from `PR_TITLE` or `HEAD_BRANCH` via regex `([A-Z0-9]+-\d+)` (case-insensitive).

If no `KEY` found: continue without it. Show the review table, but do not save a task-folder report.

### Step 4a: Fetch Task Context (Jira)

If `KEY` was found, prefer the shared `dev-get` skill for Jira task context.

Flow:
- First read `.local/tasks/[KEY]/task.md` and `.local/tasks/[KEY]/raw.md` when present.
- If they are missing or stale, run `dev-get [KEY]` to refresh the local Jira task files.
- After `dev-get`, extract at least:
  - `JIRA_SUMMARY` from the saved task files
  - `JIRA_DESCRIPTION` / requirements from the saved task files

**If `dev-get` succeeds:** use the saved Jira task content as the main fit-check source.

**If `dev-get` fails** (missing credentials, network error, Jira unavailable): note it and rely on the PR body, branch name, commit messages, and any existing local task files. Mention this limit in the report.

### Step 5: Review Across Dimensions

Analyze PR data (`FILES[]`, `DIFF`, `COMMITS[]`, `REVIEWS[]`, `PR_BODY`, `PR_TITLE`) across each dimension below.

Extra context sources:
- `--code-base`: also use `TASK_CONTEXT`, `PROJECT_CONFIGS`, and `RELATED_FILES[]`
- Jira available (Step 4a): also use `JIRA_DESCRIPTION`

**Rule — capture exact file and line for every finding.**
Every finding in the table below must include the exact source file path and line number from the diff. Reuse these exact values in Step 8. Do not guess. Verify each line from `DIFF`.

Only create inline findings for RIGHT-side added or modified diff lines.
If a finding has no valid inline review location, keep it in the report and review table, but do not post it as a PR thread in Step 8.

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

If Jira task context was fetched in Step 4a (`JIRA_DESCRIPTION`), use it as the primary source of truth:
- Does the implementation satisfy every requirement in the task description?
- Are there any requirements in the task that are not addressed in this PR?
- Does the PR scope match the task description, or is there scope creep / incomplete work?

Regardless of Jira availability:
- Does the PR title and description clearly explain what and why?
- Does the PR scope match what the branch name or task key suggests?
- Are changes scoped appropriately, or is there scope creep?
- Does `PR_BODY` reference necessary context (tickets, decisions, trade-offs)?

PR hygiene:
- Do commit messages follow the convention? (`{action} {description} KEY`)
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

Show all findings in a table sorted by Priority (Critical → Low):

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

Report format — keep exact file paths and line numbers from Step 5 for reuse in Step 8:

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

If no `KEY` was found, show the report in chat and tell the user:
```
No task key detected. Report displayed above — save manually if needed.
```

### Step 8: Post Pending Review on PR (Optional)

After the report is generated, ask the user: "Post these findings as a pending review on the PR? (yes / no)"

If `no`: skip to Step 9.

If `yes`: post each finding as a comment thread in one pending review.

**Step 8a: Get PR Node ID**

Fetch the GraphQL node ID of the pull request:
```bash
PR_NODE_ID=$(gh api graphql -f query='
query {
  repository(owner: "[OWNER]", name: "[REPO]") {
    pullRequest(number: [PR_NUMBER]) {
      id
    }
  }
}' --jq '.data.repository.pullRequest.id')
```

**Step 8b: Create the Review (body only)**

Create an empty pending review with only a body. **Do not include `event`** — this keeps it PENDING:
```bash
REVIEW_ID=$(gh api graphql --jq '.data.addPullRequestReview.pullRequestReview.id' \
  -f query='
mutation($prId: ID!, $body: String!) {
  addPullRequestReview(input: {
    pullRequestId: $prId
    body: $body
  }) {
    pullRequestReview { id state }
  }
}' \
 -f prId="$PR_NODE_ID" \
 -f body="Automated review from dev-review-pr skill. The user will review and submit.")
```

**Step 8c: Add Comment Threads**

For each finding with a specific file and line number, add a thread to the review.

**Do not re-derive file paths or line numbers.** Read them from the `## Findings` table in the feedback report or the Step 6 review table.

Before posting a thread:
- Confirm the finding maps to a valid RIGHT-side inline review location.
- Build the GraphQL variables safely using a structured JSON payload.
- Prefer a scripting tool or API client that can send nested JSON reliably.
- Do not hand-build complex JSON strings if that risks escaping errors.

GraphQL mutation shape:

```graphql
mutation($prId: ID!, $reviewId: ID!, $path: String!, $line: Int!, $body: String!) {
  addPullRequestReviewThread(input: {
    pullRequestId: $prId
    pullRequestReviewId: $reviewId
    path: $path
    line: $line
    side: RIGHT
    body: $body
  }) { thread { id } }
}
```

Rules for threads:
- `path` — the Checked File path from the findings table
- `line` — the Checked Line number in the source file, not diff position. If line is a range (for example `27-34`), use the start line.
- `side` — always `RIGHT`
- `body` — `**[Priority] Review Category** Issue Summary\n\n**Suggested:** Suggested Solution`
- Only include findings with a specific file and line number.
- Only include findings whose line is visible on the RIGHT side of the PR diff as an added or modified line.
- Skip report-level findings (line is `—`) and any finding whose inline location cannot be confirmed.

If posting a thread fails, do not retry blindly. Record the failed finding, attempted `path` and `line`, and the API error. Continue with the remaining findings when safe, then report partial success.

Do not claim full posting success unless every intended thread was created.

```
✅ Pending review created on PR #[PR_NUMBER]
   Review ID: [review_id]
   State: PENDING
   PR: [PR_URL]
   Threads posted: [POSTED_COUNT]/[INTENDED_COUNT]
```

Tell the user: "The review is pending — go to the PR page to review, edit, and submit the comments yourself."

### Step 9: Success Output

```
✅ Review complete for [PR_TITLE]

Issues found: [N] (Critical: [N], High: [N], Medium: [N], Low: [N])
Verdict: [Changes requested | Approved with suggestions | Approved]
Report: [TASK_DIR/pr-feedback-[KEY].md]
Context limits: [none | Jira unavailable, fit check based on PR metadata only | key not found, report not saved to task folder | PR data may be truncated]
Pending review: [not posted | posted [POSTED_COUNT]/[INTENDED_COUNT] threads]

PR: [PR_URL]
```

---

## Self-Check

- [ ] PR detected from URL or auto-detected from worktree?
- [ ] Failed fast when no PR found?
- [ ] All PR data fetched (files, diff, commits, reviews)?
- [ ] `--code-base` flag respected — fails fast if branch not local?
- [ ] Codebase context fetched when `--code-base` is set?
- [ ] Task key extracted when possible?
- [ ] Jira task context fetched when `.env` available?
- [ ] Fit check uses Jira requirements when available, or notes limitation when not?
- [ ] All review dimensions checked?
- [ ] Issues assigned correct priority?
- [ ] Review table sorted by priority?
- [ ] Feedback report written to task folder (when key available)?
- [ ] Verdict reflects issue severity?
- [ ] User asked about posting pending review?
- [ ] Pending review created with no `event` field?
- [ ] Threads added via `addPullRequestReviewThread` with `path`, `line`, `side: RIGHT`?
- [ ] Only RIGHT-side added/modified diff lines used for inline comments?
- [ ] Report-level findings (line = `—`) and unconfirmed inline locations skipped from comments?
- [ ] Partial thread-post failures reported accurately?
