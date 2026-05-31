---
name: dev-commit
description: Stage and commit changes in related groups, appending the task key to every commit message. Runs during dev-code or standalone.
triggers:
  - "dev-commit"
  - "devcommit"
---

## Paths

Read shared paths from `config.md`.
---

## Workflow

### Step 1: Resolve Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY. Stop if no valid KEY.

### Step 2: List Changed Files

```bash
git status --short
```

Group files by related area and chronologically by when changes were made:
- Files changed together in the same step of the conversation → group together
- Files with the same purpose (e.g. all HTML, all templates, all config) → group together
- Unrelated files → separate commits

**Order the commits by timeline — oldest changes first, newest last.**
This keeps the git history aligned with the actual work sequence.

**Rules:**
- Never commit all files in one giant commit if they span unrelated changes.
- Each commit should be one cohesive logical change.
- Show the user the proposed groups before committing.

### Step 3: Commit Each Group

For each group:

```bash
git add <file1> <file2> ...
git commit -m "<message> KEY"
```

**Message format:** `<action> <description> KEY`
- Examples: `Add dev-commit skill DEV-9`, `Fix template paths DEV-9`, `Update config for worktree DEV-9`
- Past tense for fixes (`Fixed`, `Updated`), present for new (`Add`, `Create`)
- Keep short — under 72 characters including `KEY`

**Do not use `--squash` or `--amend`.** Each commit is a normal, standalone commit.

### Step 4: Verify

```bash
git status
git --no-pager log --oneline -<N>
```

Confirm no files left uncommitted (unless intentionally skipped). Report what was committed.

### Step 5: Report

```
✅ Committed [N] groups for [KEY]

[commit 1 hash] <message>
[commit 2 hash] <message>
...

Uncommitted: [files skipped, or "none"]
```
