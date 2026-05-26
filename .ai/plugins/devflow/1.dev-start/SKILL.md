---
name: dev-start
description: Start a gitflow worktree for a Jira task. Creates a feature or hotfix branch in a sibling worktree folder, ready for development.
triggers:
  - "dev-start"
  - "devstart"
---

## Paths

Read shared paths from `config.md`. `TASKS_ROOT` and `TASK_DIR` are defined there.

- `WORKTREE_ROOT`: `[REPO_NAME]-worktrees` — sibling folder to the repo, e.g. `../proj-worktrees`

---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Feature branch from `develop` |
| `--hotfix` | Hotfix branch from `main` |
| `--force` | Branch from current branch, skip branch-state validation |
| `--dry-run` | Validate and preview without creating worktree or task folder |

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`).
- Parse flags: `--hotfix`, `--force`, `--dry-run`.
- If no KEY: ask user for a Jira task key. Stop if none provided.

### Step 2: Check for Existing Worktree

Determine the repo name:
```bash
basename $(git rev-parse --show-toplevel)
```

Check if a worktree for this task already exists (match on the task key):
```bash
find "../[REPO_NAME]-worktrees" -maxdepth 1 -type d -name "*[KEY]*" 2>/dev/null
```

If a match is found: "A worktree for `[KEY]` already exists: `[MATCHED_PATH]`. Switch to it instead: `cd [MATCHED_PATH]`". Stop.

Skip this step if `--dry-run`.

### Step 3: Validate Branch State

Run `git branch --show-current`.

| Flag | Required branch | Alert if not on this branch |
|------|----------------|----------------------------|
| (none, default) | `develop` | "You are not on `develop`. Feature branches should be created from `develop`. Switch to `develop` first or use `--force` to branch from current." |
| `--hotfix` | `main` | "You are not on `main`. Hotfix branches should be created from `main`. Switch to `main` first." |
| `--force` | any | No alert. Branch from current. |

**For `--hotfix`:** also check for uncommitted changes and that `main` is up to date:

```bash
# Check working tree is clean
git status --porcelain
```
If dirty: "Working tree has uncommitted changes. Commit or stash them before creating a hotfix from `main`." Stop.

```bash
git fetch origin main
git rev-list --count HEAD..origin/main
```
If behind: "`main` is behind origin by [N] commits. Pull latest `main` before creating a hotfix." Stop.

Stop if branch requirements not met (except `--force`, which skips all of Step 3).

### Step 4: Fetch Task Summary

Use Jira MCP to fetch the task summary and build the branch name. Jira MCP requires credentials from `.env` in the repo root (`JIRA_COMPANY_DOMAIN`, `JIRA_PROJECT_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`). If Jira MCP or `.env` is unavailable, ask user: "Short summary for branch name? (e.g. `login-with-google`)"

### Step 5: Build Branch Name

Format: `[type]/[task-key-lowercase]-[short-summary]`

Examples:
- Feature: `feature/proj-2145-adjust-pdf-text-spacing`
- Hotfix: `hotfix/proj-2145-fix-login-crash`

Rules:
- Task key: lowercase, no spaces.
- Summary: lowercase, words separated by hyphens, max 5-6 words.
- Strip special characters, keep only a-z, 0-9, and hyphens.

### Step 6: Dry-Run Preview

If `--dry-run`: display what would happen and stop. Do not create anything.

```
## Dry-Run Preview

Branch: [BRANCH_NAME]
Type: [feature | hotfix | force]
Task: [KEY]
Summary: [short-summary]

Worktree would be created at: ../[REPO_NAME]-worktrees/[BRANCH_NAME]
Task folder would be: .local/tasks/[KEY]
```

Stop here. Do not proceed to Steps 7-9.

### Step 7: Create Task Folder

Create `TASK_DIR` if it doesn't exist.
Save the Jira task summary to `TASK_DIR/task.md` if Jira MCP is available (requires `.env` with Jira credentials) and file doesn't exist.

### Step 8: Create Worktree

**Pre-flight checks:**

Check the branch name is not already in use:
```bash
git branch --list "[BRANCH_NAME]"
```
If the branch exists: "Branch `[BRANCH_NAME]` already exists. Choose a different summary or delete the old branch." Stop.

Verify the parent directory is writable:
```bash
test -w ".." && echo "WRITABLE" || echo "NOT_WRITABLE"
```
If not writable: "Parent directory `..` is not writable. Cannot create worktree root." Stop.

Create worktree root if it doesn't exist:
```bash
mkdir -p "../[REPO_NAME]-worktrees"
```

Create the worktree:
```bash
git worktree add "../[REPO_NAME]-worktrees/[BRANCH_NAME]" -b [BRANCH_NAME]
```

**If worktree creation fails:** report the error. If the task folder was created in Step 7, note it:
"Worktree creation failed. The task folder `.local/tasks/[KEY]` was already created — you may want to remove it if retrying with a different branch name."

### Step 9: Report Result

```
✅ Worktree ready: ../[REPO_NAME]-worktrees/[BRANCH_NAME]

Branch: [BRANCH_NAME]
Type: [feature | hotfix | force]
Task: [KEY]

Switch to worktree first:
  cd ../[REPO_NAME]-worktrees/[BRANCH_NAME]

Then start:
  Full flow:  /devflow [KEY]
  Plan only:  /dev-plan [KEY]
```

**Important:** All further work must be done from the worktree folder. Tell the user to `cd` into it first.
