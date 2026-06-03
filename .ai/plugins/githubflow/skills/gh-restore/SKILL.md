---
name: gh-restore
description: Discard edited files on git — restore working tree to HEAD. Use when user says "discard changes", "revert files", "undo edits", "restore", or "clean working tree".
triggers:
  - "discard changes"
  - "revert files"
  - "undo edits"
  - "restore working tree"
  - "clean working tree"
  - "gh-restore"
---

## When to use

User wants to discard local edits to tracked files. Not for commits, not for stashing — just throw away working-tree changes.

## Safety

**Destructive.** Always confirm before discarding. Never run automatically.

## Workflow

### Step 1: Show what's dirty

```bash
git status --short
```

Report to user: "N modified, M untracked, K deleted files found."

### Step 2: Ask user what to discard

Present options:

- **all** — Discard all tracked file changes (`git restore .`)
- **list** — User names specific files/directories (`git restore <path>`)
- **staged** — Unstage only, keep working tree changes (`git restore --staged [files]`)
- **untracked** — Also clean untracked files (`git clean -fd`)
- **cancel** — Do nothing

If user says "all" without being shown the status, still show status first then confirm.
If user says "list", ask "Which files?" before proceeding.

### Step 3: Discard

```bash
git restore [FILES]          # discard unstaged changes in working tree
git restore --staged [FILES] # unstage only, keep working tree copy
git clean -fd                # remove untracked files (if requested)
```

### Step 4: Confirm

```bash
git status --short
```

Report: "Working tree clean." or show remaining items.

## Rules

- Always show `git status --short` before any action.
- Always ask for confirmation. This is a one-way operation.
- Never discard without the user saying "yes" or equivalent.
- If nothing to discard, report and exit.
- Use `git restore`, not `git checkout --`. (restore is the modern command since Git 2.23)
