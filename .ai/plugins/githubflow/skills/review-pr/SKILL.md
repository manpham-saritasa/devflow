---
name: review-pr
description: Review a GitHub PR across 11 dimensions using PR metadata, diff, git history, and repo rules. Deep review with git blame is default — use --quick for diff-only.
triggers:
  - "review-pr"
  - "reviewpr"
---

## When to Use

- `/review-pr [URL]` — deep review (diff + git blame + repo rules)
- `/review-pr --quick [URL]` — quick review (PR diff only, no local clone needed)
- `/review-pr` — auto-detect PR from current branch

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Deep review — diff + git blame + agent rules + related PRs. Requires local clone. Falls back to quick if not available. |
| `--quick` | Quick review — PR diff and metadata only. No local clone needed. |

## Workflow

### Step 1: Detect PR

Parse input for a PR URL (`github.com/[OWNER]/[REPO]/pull/[NUMBER]`). Parse flag: `--code-base`.

If no URL: detect from current branch.
```bash
git branch --show-current
gh pr list --head [BRANCH] --state open --json number,title,url
```

### Step 2: Fetch PR Data

```bash
gh pr view [PR_NUMBER] --repo [OWNER]/[REPO] --json title,body,headRefName,baseRefName,state,mergeable,reviews,additions,deletions,files,commits
gh pr diff [PR_NUMBER] --repo [OWNER]/[REPO]
```

### Step 2a: Verify Codebase Match

Skip only if `--quick` flag is set.

Check that the local clone matches the PR's base branch. If no local clone or mismatch, warn user and fall back to quick review.

```bash
git rev-parse HEAD
gh api /repos/[OWNER]/[REPO]/git/ref/heads/[BASE_BRANCH] --jq '.object.sha'
```

Compare the two SHAs:
- Match → continue to Step 3.
- Mismatch → stop: "Local clone is not on the PR's base branch ([BASE_BRANCH]). Switch to [BASE_BRANCH] and pull latest first."

### Step 3: Standard Review (8 dimensions)

Review the PR diff and metadata across these dimensions. Label every finding: `[critical]`, `[high]`, `[medium]`, or `[low]`.

| # | Dimension | Check |
|---|-----------|-------|
| 1 | Fit | Does the code match the PR description and intent? |
| 2 | Quality | Readability, naming, duplication, complexity |
| 3 | Naming | Clear, consistent, follows conventions |
| 4 | Design | Alignment with patterns, separation of concerns |
| 5 | Performance | Queries, loops, memory, repeated work |
| 6 | Security | Validation, auth, injection, data exposure |
| 7 | Testing | Coverage, adequacy of verification |
| 8 | Documentation | Changelog, inline docs, README updates |

### Step 4: Deep Review (3 extra dimensions)

Skip only if `--quick` flag is set. Requires a local clone of the repository. If unavailable, warn and note in output.

#### 4a. AI Agent Rules Check

Read repo-level agent rule files if they exist:
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.rules`, `.cursor/rules/main.mdc`

Check: does the PR code follow or violate any rule in these files?
- Core rules: safety, reversibility, reuse over duplication
- Coding rules: function length, file size, parameter count, nesting depth
- Hard stops: did the PR touch auth, payments, schema, or CI/CD without documentation?
- Commit conventions: do messages follow `{action} {description} KEY` format?

#### 4b. Git History Check (30 days)

For each file in `FILES[]`:
```bash
git log --oneline --since=30.days -- [FILE_PATH]
git blame [FILE_PATH] -L [CHANGED_LINES]
```

Check:
- Were the same lines modified recently by another PR? Possible merge conflict or regression risk.
- Does the author of recent changes match the PR author? If different, risk of reverting or conflicting with recent work.
- Are there recent fixes in the same area that this PR might undo?
- Do commit messages on the same file reveal a pattern (e.g., repeated bug fixes → deeper issue)?

#### 4c. Related PR Comments Check

Find PRs that touched the same files in the last 30 days:
```bash
gh pr list --repo [OWNER]/[REPO] --state merged --search "sort:updated-desc" --limit 20 --json number,title,url,files
```

Filter PRs whose `files[]` overlap with `FILES[]` from the current PR. For each overlapping PR:
```bash
gh api /repos/[OWNER]/[REPO]/pulls/[PR_NUMBER]/comments --jq '.[] | {path, line, body, user: .user.login}'
```

Check:
- Are there review comments on those PRs that apply to the same lines or logic?
- Did a reviewer flag something in a past PR that is still present in this one?
- Are there repeated patterns of rejected changes (same suggestion made across multiple PRs)?

### Step 5: Present Review

```
## PR Review — [PR_TITLE]

### Summary
- Files: [N] | +[additions] -[deletions] | [N] commits
- Status: [OPEN / MERGED] | Reviewers: [names]

### What it does
[2-3 sentence plain-English summary of the feature/change]

| Change | Detail |
|--------|--------|
| [key change 1] | [what it does and why] |
| [key change 2] | [what it does and why] |

### Standard Findings

| # | Severity | File:Line | Issue | Suggestion |
|---|----------|-----------|-------|------------|
| 1 | [critical/high/medium/low] | path:123 | What's wrong | How to fix |

### Deep Review Findings

| # | Dimension | File:Line | Issue | Suggestion |
|---|-----------|-----------|-------|------------|
| 1 | Agent Rules | path:123 | Violates rule X | Fix |
| 2 | Git History | path:456 | Same lines changed 3x in 30 days | Investigate |
| 3 | Related PRs | path:789 | Same comment from PR #42 applies | Address |

*No findings if section is empty — note "None" for each dimension.*

### Verdict
[Changes requested | Approved with suggestions | Approved]
```

### Step 6: Output

```text
✅ Review complete for [PR_TITLE]

Standard issues: [N] (Critical: [N], High: [N], Medium: [N], Low: [N])
Deep review: [N findings | not available — no local clone]
Verdict: [Changes requested | Approved with suggestions | Approved]
PR: [PR_URL]
```

## Self-Check

- [ ] All 8 standard dimensions reviewed?
- [ ] Deep review: agent rules, git history, and related PR comments checked? (or noted as unavailable)
- [ ] Every finding has severity, location, and suggestion?
- [ ] Verdict matches findings?
- [ ] No devflow paths (TASK_DIR, config.md, .local) — only repo-root files, git, and gh CLI?
