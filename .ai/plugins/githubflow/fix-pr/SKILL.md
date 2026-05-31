---
name: fix-pr
description: Push branch and resolve GitHub PR review threads via GraphQL. Use when dev-fix-pr needs to push fixes and resolve comments.
triggers:
  - "fix-pr"
---

## Usage

Called after code fixes are committed. Pushes branch and resolves addressed threads.

```
fix-pr KEY
```

## Workflow

### Step 1: Detect Branch and PR

```bash
git branch --show-current
```

Find the open PR:
```bash
gh pr list --head [BRANCH_NAME] --state open --json number,title,url
```

No open PR → stop. Extract `OWNER`, `REPO` from PR URL.

### Step 2: Push Branch

```bash
git push origin [BRANCH_NAME]
```

### Step 3: Resolve Threads

Fetch unresolved thread IDs:
```bash
gh api graphql -f query='
query {
  repository(owner: "[OWNER]", name: "[REPO]") {
    pullRequest(number: [PR_NUMBER]) {
      reviewThreads(first: 50) {
        nodes { id isResolved path }
      }
    }
  }
}'
```

For each thread addressed by a code fix, resolve silently:
```bash
gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "[ID]"}) { thread { isResolved } } }'
```

Do NOT resolve reply-only threads — user handles those in PR UI.

### Step 4: Check for More Comments

```bash
gh api graphql -f query='
query {
  repository(owner: "[OWNER]", name: "[REPO]") {
    pullRequest(number: [PR_NUMBER]) {
      reviewThreads(first: 50) {
        nodes { id isResolved }
      }
    }
  }
}'
```

- Zero unresolved → "✅ All comments resolved."
- Some remain → "[N] comments still open."

### Step 5: Return

```
✅ Pushed. Resolved: [N]. Remaining: [N].
PR: [PR_URL]
```

## Rules

| Rule | Detail |
|------|--------|
| Commit message | `Fix PR comments [KEY]` |
| Resolve silently | Use GraphQL mutation, no reply on code-fix threads |
| Reply threads | Don't resolve via GraphQL; user handles in PR UI |
| Kept comments | If human already replied "keep it", skip |
