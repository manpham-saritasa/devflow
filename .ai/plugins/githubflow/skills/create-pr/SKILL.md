---
name: create-pr
description: Create or reuse a GitHub pull request. Pass title and body, get back PR URL. Use when dev-ship needs to open a PR, or any skill needs GitHub PR creation.
triggers:
  - "create-pr"
---

## Usage

Called with KEY, title, and body. Auto-detects branch and base.

```
create-pr KEY "TITLE" "BODY"
```

## Workflow

### Step 1: Detect Branch

```bash
git branch --show-current
```

### Step 2: Check Existing PR

```bash
gh pr list --head [BRANCH] --state open --json number,title,url,headRefName,baseRefName
```

Filter by `headRefName == [BRANCH]`.

**If open PR exists:**
- Check for new commits since last PR comment:
  ```bash
  gh pr view [PR_NUMBER] --json comments --jq '.comments[-1].createdAt'
  git log --oneline --since="[LAST_COMMENT_DATE]"
  ```
- No new commits → "✅ PR #[N] already up to date."
- New commits → post summary table:
  ```
  ## Recent Changes
  | Commit | Summary |
  |--------|---------|
  ```
  Return existing PR_URL.

**If no open PR:**

### Step 3: Push and Create

```bash
git push origin [BRANCH]
gh pr create --base [BASE_BRANCH] --head [BRANCH] --title "TITLE" --body "BODY"
```

`BASE_BRANCH` must match the repository default (`main` or `develop`). Detect via `gh repo view --json defaultBranchRef`.

### Step 4: Return

```
✅ PR: {PR_URL}
```
