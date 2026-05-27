---
name: dev-review-pr
description: Review a GitHub PR across multiple quality dimensions. Supports current and past PRs. Provides structured feedback with prioritized issues and a downloadable report.
triggers:
  - "review-pr"
  - "reviewpr"
  - "dev-review-pr"
  - "review-pr --code-base"
  - "reviewpr --code-base"
---

## When to Use

- `/review-pr [URL]` — review a specific PR (past or current)
- `/review-pr` or `/reviewpr` — auto-detect task key from worktree and find the open PR
- `/reviewpr [URL]` — shorthand with URL
- `/review-pr --code-base` or `/reviewpr --code-base` — review PR against the local codebase too. Fails fast if not on the correct worktree/branch.

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Fetch and review from PR data only (files, diff, commits, reviews) |
| `--code-base` | Also checks local task context, project conventions, and related source files. Fails if HEAD branch doesn't exist locally. |

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT` and `TASK_DIR` variables are defined there.

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

### Step 3a: Check Codebase (if `--code-base`)

Skip this step if `--code-base` flag is not set.

**Fail fast — verify we're on the right branch:**
```bash
git branch --list "[HEAD_BRANCH]"
```
If no output: "The `[HEAD_BRANCH]` branch does not exist locally. Switch to the correct worktree first." Stop.

**Fetch codebase context:**

Task context — read requirements and plan if available:
```bash
cat .local/tasks/[KEY]/task.md 2>/dev/null || echo "No task folder found"
cat .local/tasks/[KEY]/plan.md 2>/dev/null || echo "No plan found"
```

Project conventions — check for linters and configs:
```bash
ls .editorconfig .phpcs.xml .phpcs.xml.dist .eslintrc* tsconfig.json .rubocop.yml .prettierrc* 2>/dev/null || echo "No project linting configs found"
```

Related files — for each changed file in `FILES[]`, list siblings in the same directory:
```bash
for file in [FILES]; do
  dir=$(dirname "$file")
  echo "-- $dir/"
  ls "$dir/" 2>/dev/null
done
```

Store these as `TASK_CONTEXT`, `PROJECT_CONFIGS`, and `RELATED_FILES[]` for use in review dimensions below.

### Step 4: Extract Task Key

If `KEY` was already extracted from the branch name in Step 1, use it.

Otherwise, extract `KEY` from `PR_TITLE` or `HEAD_BRANCH` via regex `([A-Z0-9]+-\d+)` (case-insensitive).

If no `KEY` found: continue without it (the report will not be saved to a task folder, but the table review will still be shown).

### Step 4a: Fetch Task Context (Jira)

If `KEY` was found, attempt to fetch the Jira task description for fit check context. This requires `.env` in the repo root with Jira credentials:

```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_PROJECT_KEY=RMASUP
JIRA_EMAIL=john.doe@saritasa.com
JIRA_API_TOKEN=ATATT3xFfGF0eq6-JnkSzR-Example
```

If `.env` exists and has all required fields:
```bash
source .env
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://$JIRA_COMPANY_DOMAIN.atlassian.net/rest/api/3/issue/$KEY" \
  | jq '{summary: .fields.summary, description: .fields.description, acceptanceCriteria: .fields.customfield_*}' 2>/dev/null || echo "Jira fetch failed"
```

Parse the result:
- `JIRA_SUMMARY` — task title
- `JIRA_DESCRIPTION` — task description / requirements
- `JIRA_ACCEPTANCE_CRITERIA` — acceptance criteria if available

**If Jira fetch succeeds:** use `JIRA_DESCRIPTION` and `JIRA_ACCEPTANCE_CRITERIA` in the Fit Check (Step 5a) to verify the PR changes match the actual task requirements.

**If Jira fetch fails** (no `.env`, missing credentials, network error): note it and rely on the PR body, branch name, and commit messages for context. The fit check will be less thorough — mention this limitation in the report.

### Step 5: Review Across Dimensions

Analyze the PR data (`FILES[]`, `DIFF`, `COMMITS[]`, `REVIEWS[]`, `PR_BODY`, `PR_TITLE`) across every dimension below. For each issue found, assign:

If `--code-base` was used, also leverage `TASK_CONTEXT`, `PROJECT_CONFIGS`, and `RELATED_FILES[]` for deeper analysis against actual project code.

**Rule — capture exact file and line for every finding.**
Every finding in the table below must include the precise source file path and line number from the diff. These exact values will be reused in Step 8 to post review comments. Do not use approximate or remembered values — verify each line number from the `DIFF` output during the review.

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

If Jira task context was fetched in Step 4a (`JIRA_DESCRIPTION`, `JIRA_ACCEPTANCE_CRITERIA`), use it as the primary source of truth:
- Does the implementation satisfy every acceptance criterion?
- Are there any requirements in the task that are not addressed in this PR?
- Does the PR scope match the task description, or is there scope creep / incomplete work?

Regardless of Jira availability:
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

Report format — the `## Findings` table preserves the exact file paths and line numbers from Step 5 for reuse in Step 8:

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

### Step 8: Post Pending Review on PR (Optional)

After the report is generated, ask the user: "Post these findings as a pending review on the PR? (yes / no)"

If `no`: skip to Step 9.

If `yes`: post each finding as a comment thread in a single pending (unsubmitted) review.

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

Create an empty pending review with just a body. **Do not include `event`** — this keeps it in PENDING state:
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

For each finding that has a specific file and line number, add a thread to the review. Use Python to build the JSON payload since bash has trouble with complex nested JSON:

**Do not re-derive file paths or line numbers.** Read them directly from the `## Findings` table in the feedback report or the review table shown in Step 6. The values were verified against the diff in Step 5.

```python
import json, subprocess

threads = [
    {
        "path": "src/Example.cs",
        "line": 42,
        "body": "**[Medium] Fit Check** Issue summary\n\n**Suggested:** Suggested solution"
    },
]

query = '''mutation($prId: ID!, $reviewId: ID!, $path: String!, $line: Int!, $body: String!) {
  addPullRequestReviewThread(input: {
    pullRequestId: $prId
    pullRequestReviewId: $reviewId
    path: $path
    line: $line
    side: RIGHT
    body: $body
  }) { thread { id } }
}'''

for t in threads:
    payload = {
        'query': query,
        'variables': {
            'prId': '[PR_NODE_ID]',
            'reviewId': '[REVIEW_ID]',
            'path': t['path'],
            'line': t['line'],
            'body': t['body']
        }
    }
    result = subprocess.run(
        ['gh', 'api', 'graphql', '--input', '-'],
        input=json.dumps(payload), capture_output=True, text=True
    )
```

Rules for threads:
- `path` — the Checked File path from the findings table
- `line` — the Checked Line number in the source file (not diff position). If line is a range (e.g. `27-34`), use the start line.
- `side` — always `RIGHT` (the new version of the file)
- `body` — `**[Priority] Review Category** Issue Summary\n\n**Suggested:** Suggested Solution`
- Only include findings with a specific file and line number. Skip report-level findings (line is `—`).

```
✅ Pending review created on PR #[PR_NUMBER]
   Review ID: [review_id]
   State: PENDING
   PR: [PR_URL]
```

Tell the user: "The review is pending — go to the PR page to review, edit, and submit the comments yourself."

### Step 9: Success Output

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
- [ ] Report-level findings (line = `—`) skipped from comments?
