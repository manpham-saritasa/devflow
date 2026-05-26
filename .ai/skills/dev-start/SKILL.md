---
name: dev-start
description: Start a gitflow worktree for a Jira task. Creates a feature or hotfix branch in a sibling worktree folder, ready for development.
triggers:
  - "dev-start"
  - "devstart"
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]`
- WORKTREE_ROOT: `[REPO_NAME]-worktrees` — sibling folder to the repo, e.g. `../proj-api-worktrees`

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`).
- Parse flags: `--hotfix` (branch from main), `--force` (branch from current branch).
- If no KEY: ask user for a Jira task key. Stop if none provided.

### Step 2: Validate Branch State

Run `git branch --show-current`.

| Flag | Required branch | Alert if not on this branch |
|------|----------------|----------------------------|
| (none, default) | `develop` | "You are not on `develop`. Feature branches should be created from `develop`. Switch to `develop` first or use `--force` to branch from current." |
| `--hotfix` | `main` | "You are not on `main`. Hotfix branches should be created from `main`. Switch to `main` first." |
| `--force` | any | No alert. Branch from current. |

**For `--hotfix`:** also check `main` is up to date:
```bash
git fetch origin main
git rev-list --count HEAD..origin/main
```
If behind: "`main` is behind origin by [N] commits. Pull latest `main` before creating a hotfix."

Stop if branch requirements not met (except `--force`).

### Step 3: Fetch Task Summary

Try to get a short summary from Jira MCP or the PR body to build the branch name. If unavailable, ask user: "Short summary for branch name? (e.g. `login-with-google`)"

### Step 4: Build Branch Name

Format: `[type]/[task-key-lowercase]-[short-summary]`

Examples:
- Feature: `feature/rmasup-2145-adjust-pdf-text-spacing`
- Hotfix: `hotfix/rmasup-2145-fix-login-crash`

Rules:
- Task key: lowercase, no spaces.
- Summary: lowercase, words separated by hyphens, max 5-6 words.
- Strip special characters, keep only a-z, 0-9, and hyphens.

### Step 5: Create Task Folder

Create `TASK_DIR` if it doesn't exist.
Save the Jira task summary to `TASK_DIR/task.md` if Jira MCP is available and file doesn't exist.

### Step 6: Create Worktree

Determine the repo name:
```bash
basename $(git rev-parse --show-toplevel)
```

Create worktree root if it doesn't exist:
```
mkdir -p ../[REPO_NAME]-worktrees
```

Create the worktree:
```bash
git worktree add ../[REPO_NAME]-worktrees/[BRANCH_NAME] -b [BRANCH_NAME]
```

### Step 7: Setup Worktree

```bash
cd ../[REPO_NAME]-worktrees/[BRANCH_NAME]
```

Copy `.env` from the main repo if it exists:
```bash
cp ../../.env .env 2>/dev/null || echo "No .env found to copy"
```

### Step 8: Report Result

```
✅ Worktree ready: ../[REPO_NAME]-worktrees/[BRANCH_NAME]

Branch: [BRANCH_NAME]
Type: [feature | hotfix | force]
Task: [KEY]
Env: [.env copied | no .env found]

Switch to worktree first:
  cd ../[REPO_NAME]-worktrees/[BRANCH_NAME]

Then open:
  code .

Then start:
  /devflow [KEY]
```

**Important:** All further work must be done from the worktree folder. Tell the user to `cd` into it first.
