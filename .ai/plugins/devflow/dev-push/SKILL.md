---
name: dev-push
description: Stage and commit all changes using dev-commit, then push to origin. Quick ship for WIP or small fixes.
triggers:
  - "dev-push"
  - "dpush"
---

## When to Use

- `dev-push` or `dpush` — commit all changes and push to origin
- Quick workflow for work-in-progress or small changes

## Workflow

### Step 1: Check for Changes

```bash
git status --short
```

If clean: "Nothing to commit. Already up to date." Stop.

### Step 2: Run dev-commit

Use the `dev-commit` skill to stage and commit all changes. Let dev-commit handle the commit message, grouping, and staging logic. Do not write your own commit — delegate to the skill.

### Step 3: Verify Commit

```bash
git log -1 --oneline
```

If no new commit was created: "Nothing was committed. Push skipped." Stop.

### Step 4: Push

```bash
git push origin $(git branch --show-current)
```

Show the pushed commit and branch:
```
✅ Pushed to origin/[branch]:
   [commit-hash] [message]
```

## Self-Check

- [ ] Uncommitted changes detected?
- [ ] dev-commit ran and produced a commit?
- [ ] Pushed to current branch?
