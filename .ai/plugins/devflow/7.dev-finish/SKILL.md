---
name: dev-finish
description: Finish a gitflow worktree for a Jira task. Merges the PR, deletes the worktree, and cleans up the local branch.
triggers:
  - "dev-finish"
  - "devfinish"
---

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT` and `TASK_DIR` variables are defined there.

---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Merge PR if approved, then delete worktree and branch |
| `--worktree-only` | Delete worktree and branch only, skip PR merge |
| `--dry-run` | Preview what would happen without making changes (read-only) |

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`, case-insensitive).
- Parse flags: `--worktree-only`, `--dry-run`.
- If no KEY: detect from the current directory (see Step 2).

### Step 2: Find the Worktree

List all worktrees:
```bash
git worktree list
```

Parse each line as whitespace-separated columns: `<path> <HEAD-hash> [<branch>]`.

Example output:
```
E:/devflow                           abc1234 [main]
E:/devflow-worktrees/dev-7-foo       def5678 [feature/dev-7-update-skill]
```

**If KEY was provided:** find the line whose path or branch contains the KEY (case-insensitive).

**If no KEY was provided:** find the line whose path matches the current directory (case-insensitive comparison, normalize path separators). Extract KEY from the branch name on that line (regex: `([A-Z0-9]+-\d+)`, case-insensitive). If no KEY can be extracted from the branch name, stop: "Cannot detect task key from the current directory. Provide a KEY: `dev-finish [KEY]`."

Extract from the matching line:
- `WORKTREE_PATH` — first column (the directory path)
- `BRANCH_NAME` — the branch name in brackets
- `MAIN_REPO` — the path from the line whose branch is `main` (or `develop` if no `main` worktree exists)

**If no match:** "No worktree found for `[KEY]` on this machine." Stop.

**If multiple matches:** show all and ask user to pick one.

### Step 3: Check PR Status (Read-Only)

Find the open PR for this branch (`gh pr` works from any directory):
```bash
gh pr list --head "[BRANCH_NAME]" --state open --json number,title,url,reviewDecision
```

| Result | Action |
|--------|--------|
| No open PR | `PR_STATUS` = `no PR found`. "No open PR found for branch `[BRANCH_NAME]`." |
| Multiple PRs | Show all, ask user to pick one, then use its status. |
| Single PR | `PR_STATUS` = the `reviewDecision` value (may be `APPROVED`, `CHANGES_REQUESTED`, `REVIEW_REQUIRED`, or blank/null). |

If `reviewDecision` is blank or null, treat it as `REVIEW_REQUIRED` (no reviews submitted yet).

Save `PR_URL` and `PR_NUMBER` for later steps.

### Step 4: Dry-Run Preview

If `--dry-run`: display what would happen and stop.

```
## Dry-Run Preview

Task: [KEY]
Worktree: [WORKTREE_PATH]
Branch: [BRANCH_NAME]
Main repo: [MAIN_REPO]

PR: [PR_URL | no PR found]
PR status: [PR_STATUS]

Action: [merge PR + delete worktree | delete worktree only | no action (blocked)]
```

Stop here. Do not proceed to Steps 5-8.

### Step 5: Handle PR

Skip this step if `--worktree-only`.

| PR_STATUS | Action |
|-----------|--------|
| `no PR found` | "No open PR found for branch `[BRANCH_NAME]`. It may already be merged. Proceeding to clean up worktree." Continue to Step 6. |
| `APPROVED` | Merge the PR (proceed to Step 5a) |
| `CHANGES_REQUESTED` | "PR has requested changes. Resolve them before finishing: [PR_URL]" Stop. |
| `REVIEW_REQUIRED` | "PR is awaiting review. Cannot merge yet: [PR_URL]" Stop. |
| blank / null | "PR has no reviews yet. Cannot merge: [PR_URL]" Stop. |

#### Step 5a: Merge the PR

```bash
gh pr merge [PR_NUMBER] --squash --delete-branch
```

If merge fails: report the error and stop. Do not delete the worktree.

```
✅ PR merged: [PR_URL]
```

### Step 6: Delete Worktree

Check if the current working directory is inside the worktree:
```bash
pwd
```
If `pwd` starts with `[WORKTREE_PATH]`, set `WAS_IN_WORKTREE = true`. The user's shell will be in a deleted directory after this step — they'll need to `cd` out.

Remove the worktree from git tracking (use `-C` so the command runs from the main repo, regardless of cwd):
```bash
git -C "[MAIN_REPO]" worktree remove "[WORKTREE_PATH]" --force
```

Delete the entire worktree folder from disk (ensures any untracked or gitignored files are also removed):
```bash
rm -rf "[WORKTREE_PATH]"
```

Delete the local branch (it may still exist after worktree removal):
```bash
git -C "[MAIN_REPO]" branch -D "[BRANCH_NAME]" 2>/dev/null
```
If branch deletion fails (already deleted by PR merge, or never existed), ignore the error.

### Step 7: Write Changelog and Update Progress

Skip if `--dry-run`.

**Write `TASK_DIR/changelog.md`:** Append a new iteration recording the finish action. Use the same iteration-number-as-heading format used by other skills:
- `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- `**Trigger:** dev-finish — PR merged, worktree cleaned up`
- Record PR URL, merge status, worktree removal, branch deletion
- Create the file if it doesn't exist

**Update `TASK_DIR/progress.md`:**
- If exists: prepend status "Finished", PR URL, timestamp
- Else: create new file with status "Finished"

### Step 8: Report Result

```
✅ dev-finish complete for [KEY]

PR: [PR_URL | skipped | no PR found]
Worktree removed: [WORKTREE_PATH]
Branch deleted: [BRANCH_NAME]
Changelog: .local/tasks/[KEY]/changelog.md
Progress: .local/tasks/[KEY]/progress.md
```

If `WAS_IN_WORKTREE = true`, add:
```
⚠️  Your shell is in a deleted directory. Switch to the main repo:
  cd [MAIN_REPO]
```

---

## Edge Cases

- **Worktree not found:** fail fast with a clear message.
- **KEY not extractable from branch name:** stop and ask user to provide KEY explicitly.
- **No `main` worktree:** fall back to `develop` for `MAIN_REPO`. If neither exists, use the first worktree listed.
- **`gh` CLI not installed:** stop and tell user to install it (`gh auth login`).
- **No open PR:** assume already merged, proceed to cleanup.
- **PR has unresolved comments / changes requested:** stop and show PR URL.
- **PR with no reviews (null reviewDecision):** treat as `REVIEW_REQUIRED`, stop.
- **Merge fails:** stop, keep worktree intact, show error.
- **Multiple worktrees matching KEY:** let user choose.
- **Running from the worktree itself:** detect via `pwd`, warn the user their shell is in a deleted directory and show the `cd` command to escape.
