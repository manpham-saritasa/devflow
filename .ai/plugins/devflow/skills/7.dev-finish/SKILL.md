---
name: dev-finish
description: Finish a gitflow branch for a Jira task. Defaults to gitflow mode (branch in main clone). Supports worktree mode (--worktree). Merges the PR, deletes the worktree (if applicable), and cleans up the local branch.
triggers:
  - "dev-finish"
  - "devfinish"
---

## Paths

Read shared paths from `config.md`.
---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Merge PR if approved, then delete worktree/branch |
| `--worktree-only` | Delete worktree/branch only, skip PR merge |
| `--gitflow` | Gitflow mode (default) — branch in main clone, skip worktree cleanup |
| `--worktree` | Worktree mode — cleanup worktree folder + branch |
| `--dry-run` | Preview what would happen without making changes (read-only) |

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`, case-insensitive).
- Parse flags: `--worktree-only`, `--worktree`, `--dry-run`.
- If no KEY: detect from the current directory (see Step 2).

**Mode:** `--worktree` for worktree, default is gitflow.

### Step 2: Find the Branch

**Worktree mode:**

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

**Gitflow mode:**

List all local branches:
```bash
git branch --list "*[KEY]*"
```

If no match: "No branch found for `[KEY]`. Provide a KEY: `dev-finish [KEY]`". Stop.

If multiple matches: show all and ask user to pick one.

Extract:
- `BRANCH_NAME` — the matched branch name
- `MAIN_REPO` — the current repo root (`git rev-parse --show-toplevel`)

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

Mode: [worktree | gitflow]
Task: [KEY]
[Worktree mode: Worktree: [WORKTREE_PATH]]
Branch: [BRANCH_NAME]
Main repo: [MAIN_REPO]

PR: [PR_URL | no PR found]
PR status: [PR_STATUS]

Action: [merge PR + delete worktree | merge PR + delete branch | delete worktree only | delete branch only | no action (blocked)]
```

Stop here. Do not proceed to Steps 5-7.

### Step 5: Handle PR

Skip this step if `--worktree-only`.

| PR_STATUS | Action |
|-----------|--------|
| `no PR found` | "No open PR found for branch `[BRANCH_NAME]`. It may already be merged. Proceeding to clean up worktree." Continue to Step 6. |
| `APPROVED` | Merge the PR (proceed to Step 5a) |
| `CHANGES_REQUESTED` | "PR has requested changes. Resolve them before finishing: [PR_URL]" Stop. |
| `REVIEW_REQUIRED` | "PR is awaiting review. Cannot merge yet: [PR_URL]" Stop. |
| blank / null | "PR has no reviews yet. Cannot merge: [PR_URL]" Stop. |

#**Merge the PR:**

Use the merge strategy from `config.md` (`MERGE_STRATEGY`, defaults to `--merge` which preserves full commit history):

```bash
gh pr merge [PR_NUMBER] [MERGE_STRATEGY] --delete-branch
```

If merge fails: report the error and stop. Do not delete the worktree.

```
✅ PR merged: [PR_URL]
```

**Update Jira:** Call `jira-move` with `KEY` and milestone `ready-for-qa` (non-blocking).

### Step 6: Cleanup

**Worktree mode:**

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

**Gitflow mode:**

Switch to base branch first so you are not on the branch being deleted:
```bash
git checkout [BASE_BRANCH]
```

Where `BASE_BRANCH`:
| PR base | `main` or `develop` from `gh pr view` |
| No PR | `develop` (default) |

Delete the local branch:
```bash
git branch -D "[BRANCH_NAME]" 2>/dev/null
```
If branch deletion fails (already deleted by PR merge, or never existed), ignore the error.

Delete the remote branch (only if PR was merged):
```bash
git push origin --delete "[BRANCH_NAME]" 2>/dev/null
```
Skip this step if no PR was found or PR was not merged. If deletion fails (already deleted, no remote, or no permission), ignore the error.

### Step 7: Report Result

**Worktree mode:**
```
✅ dev-finish complete for [KEY]

PR: [PR_URL | skipped | no PR found]
Worktree removed: [WORKTREE_PATH]
Branch deleted: [BRANCH_NAME]
```

If `WAS_IN_WORKTREE = true`, add:
```
⚠️  Your shell is in a deleted directory. Switch to the main repo:
  cd [MAIN_REPO]
```

**Gitflow mode:**
```
✅ dev-finish complete for [KEY]

PR: [PR_URL | skipped | no PR found]
Branch deleted (local): [BRANCH_NAME]
[Branch deleted (remote): [BRANCH_NAME] — only if PR was merged]
Switched to: [BASE_BRANCH]
```

---

## Edge Cases

- **Branch/worktree not found:** fail fast with a clear message.
- **Remote branch still exists after PR merge:** `dev-finish` deletes it with `git push origin --delete` only after confirming the PR was merged. Not deleted if PR is skipped or still open.
- **KEY not extractable from branch name:** stop and ask user to provide KEY explicitly.
- **No `main` worktree:** fall back to `develop` for `MAIN_REPO`. If neither exists, use the first worktree listed.
- **`gh` CLI not installed:** stop and tell user to install it (`gh auth login`).
- **No open PR:** assume already merged, proceed to cleanup.
- **PR has unresolved comments / changes requested:** stop and show PR URL.
- **PR with no reviews (null reviewDecision):** treat as `REVIEW_REQUIRED`, stop.
- **Merge fails:** stop, keep worktree intact, show error.
- **Multiple worktrees matching KEY:** let user choose.
- **Running from the worktree itself:** detect via `pwd`, warn the user their shell is in a deleted directory and show the `cd` command to escape.
- **Task folder is kept:** `.local/tasks/[KEY]/` is intentionally preserved after finish. It contains plan, changelog, review, and PR feedback reports — useful as a snapshot of completed work.
