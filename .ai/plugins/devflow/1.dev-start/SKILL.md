---
name: dev-start
version: 0.1.0
description: Start a gitflow branch for a Jira task. Defaults to gitflow mode (branch in main clone). Supports worktree mode (--worktree). Creates feature, hotfix, or release branches.
triggers:
  - "dev-start"
  - "devstart"
  - "dev start"
---

## Paths

Read shared paths from `config.md`.

## When to Use

- `dev-start KEY` — feature branch from develop
- `dev-start KEY summary` — feature branch with custom summary (skips Jira fetch)
- `dev-start KEY --hotfix` — hotfix from main
- `dev-start KEY --release` — release branch
- `dev-start KEY --worktree` — isolated worktree
- `dev-start KEY --dry-run` — preview only

### Worktree folder hierarchy

When you run `dev-start PROJ-2145` from the main repo, it creates a sibling worktree folder. The resulting layout looks like this:

```
proj-api\							← the main repo
proj-api-worktrees\					← all worktrees live here (flat — no type subfolders)
├── proj-111-adjust-text\			← worktree 1 (branch: feature/proj-111-...)
│   ├── .ai\
│   ├── src\
│   └── .env
├── proj-222-login-google\			← worktree 2 (branch: feature/proj-222-...)
├── proj-333-update-button\			← worktree 3 (branch: hotfix/proj-333-...)
└── proj-444-login-issue\			← worktree 4 (branch: hotfix/proj-444-...)
```

The worktree directory uses only the short name (without the type prefix), while the git branch keeps the full `type/key-summary` format.
All development happens inside the worktree — the main repo stays clean.

---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Feature branch from `develop` |
| `--hotfix` | Hotfix branch from `main` |
| `--release` | Release branch from `develop` |
| `--force` | Branch from current branch, skip branch-state validation |
| `--gitflow` | Gitflow mode (default) — branch in main clone |
| `--worktree` | Worktree mode — create sibling worktree folder |
| `--dry-run` | Validate and preview without creating worktree or task folder |

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`).
- Parse flags: `--hotfix`, `--release`, `--force`, `--worktree`, `--dry-run`.
- Remaining words after KEY and flags become the summary (used in Step 4).
- If no KEY: ask user for a Jira task key. Stop if none provided.

**Mode:** `--worktree` for worktree, default is gitflow.

**Output to user:** Show `[KEY]` parsed, `[MODE]` selected, and the expected branch type. Do not show branch name yet (built in Step 5).

### Step 2: Check for Existing Branch

**Worktree mode:**
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

**Gitflow mode:**
Check if a local branch for this task already exists:
```bash
git branch --list "*[KEY]*"
```

If a match is found: "A branch for `[KEY]` already exists: `[MATCHED_BRANCH]`. Switch to it: `git checkout [MATCHED_BRANCH]`". Stop.

If no local match, check remote:
```bash
git ls-remote --heads origin "*[KEY]*"
```

If found on remote: "Task `[KEY]` already started on remote: `[BRANCH]`. Checkout instead? (yes / no)"
- If yes: `git fetch origin [BRANCH] && git checkout [BRANCH]`. Stop.
- If no: continue creating a new branch.

### Step 3: Validate Branch State

Run `git branch --show-current`.

| Flag | Required branch | Alert if not on this branch |
|------|----------------|----------------------------|
| (none, default) | `develop` | "Feature branches must start from `develop`. Switch to `develop` first or use `--force` to branch from current." |
| `--hotfix` | `main` | "Hotfix branches must start from `main`. Switch to `main` first." |
| `--release` | `develop` | "Release branches must start from `develop`. Switch to `develop` first or use `--force`." |
| `--force` | any | No alert. Branch from current. |

When auto-hotfix mode is active (single-branch repo), the `--hotfix` row applies instead of the default.

**Single-branch repos (no `develop`):** When no flags are set and `develop` does not exist locally or on remote, but `main` does, auto-switch to hotfix mode. Branch from `main` using hotfix naming (`hotfix/[key]-[summary]`). No prompt needed. The base branch for Step 8 becomes `main`.

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

### Step 4: Resolve Task Summary

Check if the user provided a summary alongside the key in the original input (e.g. `dev-start DEV-15 login-with-google`). Extract anything after the KEY as the summary.

**If user provided a summary:** Use it directly. Skip Jira fetch — no need to query. Format: lowercase, words separated by hyphens. Proceed to Step 5.

**If no summary provided:** Prefer the shared `dev-get` skill to fetch Jira task context. Read `.local/tasks/[KEY]/task.md` and `.local/tasks/[KEY]/raw.md` when present.

If the task files are missing, run `dev-get [KEY]` to populate them, then use the saved Jira summary to build the branch name.

If `dev-get` cannot run or task files still do not exist, ask user: "Short summary for branch name? (e.g. `login-with-google`)"

### Step 5: Build Branch Name

Format: `[type]/[task-key-lowercase]-[short-summary]`

Examples:
- Feature: `feature/proj-2145-adjust-pdf-text-spacing`
- Hotfix: `hotfix/proj-2145-fix-login-crash`
- Release: `release/proj-2145-version-2-1-0`

Rules:
- Task key: lowercase, no spaces.
- Summary: lowercase, words separated by hyphens, max 5-6 words.
- Strip special characters, keep only a-z, 0-9, and hyphens.

### Step 5a: Compute Short Name

**Worktree mode only.** Extract the short name from the branch name (strip the type prefix):
```bash
SHORT_NAME=$(basename "[BRANCH_NAME]")
```

Example: `feature/proj-2145-adjust-text` → `proj-2145-adjust-text`

This short name is used for the worktree directory path. The full branch name is kept for git.

**Gitflow mode:** skip this step — no worktree folder needed.

### Step 6: Dry-Run Preview

If `--dry-run`: display what would happen and stop. Do not create anything.

```
## Dry-Run Preview

Mode: [worktree | legacy]
Branch: [BRANCH_NAME]
Type: [feature | hotfix | release | force]
Task: [KEY]
Summary: [short-summary]
[Worktree mode: Worktree would be created at: ../[REPO_NAME]-worktrees/[SHORT_NAME]]
[Gitflow mode: Branch would be created in main repo]
Task folder would be: .local/tasks/[KEY]
```

Stop here. Do not proceed to Steps 7-9.

### Step 7: Create Task Folder

Create `TASK_DIR` if it doesn't exist.
If `TASK_DIR/task.md` or `TASK_DIR/raw.md` is missing, prefer running `dev-get [KEY]` to populate the task folder before continuing.

### Step 8: Create Branch

**Output to user:** `✅ New branch created: [BRANCH_NAME]` before proceeding to next steps.

Always fetch and pull the base branch before creating the worktree to ensure the worktree starts from the latest source.

Determine the base branch based on flags:

| Flag | Base branch |
|------|-------------|
| (none, default) | `develop` |
| `--hotfix` | `main` |
| `--release` | `develop` |
| `--force` | current branch (`git branch --show-current`) |

When auto-hotfix mode is active (single-branch repo), `main` is used as the base branch.

### Pre-flight

```bash
git fetch origin [BASE_BRANCH]
git pull origin [BASE_BRANCH]
```

If fetch or pull fails: "Failed to fetch/pull `[BASE_BRANCH]`. Check your network connection or remote configuration." Stop.

---

### Branch name check

Check the branch name is not already in use:
```bash
git branch --list "[BRANCH_NAME]"
```
If the branch exists: "Branch `[BRANCH_NAME]` already exists. Choose a different summary or delete the old branch." Stop.

**Worktree mode:**

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
git worktree add "../[REPO_NAME]-worktrees/[SHORT_NAME]" -b [BRANCH_NAME]
```

**After worktree creation — show full path:**

Resolve and display the absolute path so the user can copy it directly:
```bash
FULL_PATH=$(cd "../[REPO_NAME]-worktrees/[SHORT_NAME]" && pwd)
echo "Full path: $FULL_PATH"
```

**Copy `.env` and `.env.local`:**

Copy environment files from the repo root to the new worktree:

```bash
if [ -f ".env" ]; then
    cp ".env" "$FULL_PATH/.env"
fi
if [ -f ".env.local" ]; then
    cp ".env.local" "$FULL_PATH/.env.local"
fi
```

If neither file exists, skip this step silently (not all projects use them).

`.env.local` is the recommended location for Jira credentials (`JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL`) used by `dev-get`. It is automatically gitignored via the standard `.env.*` pattern and never committed.

If worktree creation fails: report the error and note the task folder was already created.

**Gitflow mode:**

Create the branch directly in the main clone:
```bash
git checkout -b [BRANCH_NAME]
```

If branch creation fails: report the error and note the task folder was already created.

### Step 9: Report Result

**Worktree mode:**
```
✅ Worktree ready: ../[REPO_NAME]-worktrees/[SHORT_NAME]
   Full path: [resolved absolute path]

Branch: [BRANCH_NAME]
Type: [feature | hotfix | release | force]
Task: [KEY]

Switch to worktree first:
  cd ../[REPO_NAME]-worktrees/[SHORT_NAME]

Then start:
  Full flow:  /devflow [KEY]
  Plan only:  /dev-plan [KEY]
```

**Important:** All further work must be done from the worktree folder. Always `cd ../[REPO_NAME]-worktrees/[SHORT_NAME]` before running any dev commands.

**Gitflow mode:**
```
✅ Branch ready: [BRANCH_NAME]

Type: [feature | hotfix | release | force]
Task: [KEY]

You are already on the branch. Start:
  Full flow:  /devflow [KEY]
  Plan only:  /dev-plan [KEY]
```

### Step 10: Update Jira Status `[hook — non-critical]`

Call `jira-move` skill with `KEY` and milestone `in-progress`. Non-blocking — continue on failure.
