---
name: dev-fix-pr
description: Fix GitHub PR review comments. Lists unresolved comments, plans fixes, applies changes, and resolves threads. Supports multiple rounds — loops until all comments are resolved.
triggers:
  - "dev-fix-pr"
  - "dev-fix-pr --dry-run"
  - "devfixpr"
  - "devfixpr --dry-run"
  - "dev fix pr"
---

## Paths

Read shared paths from `config.md`.
---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Plan, apply, commit locally, then push + resolve after approval |
| `--dry-run` | Fetch comments and show the proposed plan only. Do not edit, commit, push, reply, or resolve threads. |

---

## Workflow

### Step 1: Detect Branch and PR

Parse flags: `--dry-run`.

**First, try the worktree path:**
```bash
git worktree list
```

If the current directory (`pwd`) appears in the output and the branch is not `main` or `develop`:
- `BRANCH_NAME` — the branch name in brackets
- Continue to PR lookup below.

**Legacy fallback — not in a worktree, on a regular branch:**
```bash
git branch --show-current
```

If the current branch is not `main` or `develop`, use it as `BRANCH_NAME`.

**If neither path yields a branch:** stop — "Not on a feature/hotfix branch and not in a worktree. Switch to your task branch or worktree first."

**Find the open PR for this branch:**
```bash
gh pr list --head "[BRANCH_NAME]" --state open --json number,title,url
```

| Result | Action |
|--------|--------|
| No open PR | "No open PR found for branch `[BRANCH_NAME]`. Create a PR first or check the branch name." Stop. |
| Single PR | Save `PR_NUMBER`, `PR_URL`. Continue. |
| Multiple PRs | Show all and ask user to pick one. |

Extract `OWNER` and `REPO` from the PR URL:
```
https://github.com/[OWNER]/[REPO]/pull/[NUMBER]
```

### Step 2: List Unresolved Comments (§1)

Fetch unresolved review threads from the PR. Include `url` on each comment for clickable links:
```bash
gh api graphql -f query='
query {
  repository(owner: "[OWNER]", name: "[REPO]") {
    pullRequest(number: [PR_NUMBER]) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 10) {
            nodes {
              author { login }
              body
              url
            }
          }
        }
      }
    }
  }
}'
```

Filter to threads where `isResolved` is `false`. If a human has already replied with a decision to defer or keep (e.g., "Keep it for now"), skip that thread — it's already handled.

Present unresolved threads in a table. Use the first comment's `url` for the clickable link:

| # | File | Author | Comment |
|---|------|--------|---------|
| 1 | `[path]:[line]` — [view]([COMMENT_URL]) | @author | First line of comment body |

If no unresolved threads: "✅ No unresolved comments on this PR." Stop.

**Checkpoint:** "[N] unresolved comments found. Review the list above. Proceed to plan fixes? (yes / no)"

- `yes` → Step 3.
- `no` → stop.

### Step 3: Plan Fixes (§2)

For each unresolved comment, classify and propose:

- **Easy fix**: Single-line change, typo, rename, or already resolved in a later commit → auto-propose.
- **Non-trivial**: Logic change, new file, deletion, multi-file, or ambiguous → mark as "Ask user" in the plan table. After the plan table is shown, ask about each non-trivial item one by one before the checkpoint.
- **Reply only**: No code change needed → draft a reply.

Present the plan in a table:

| # | File | Author | Comment | Proposed Change |
|---|------|--------|---------|-----------------|
| 1 | `[path]:[line]` | @author | summary | [auto-proposed fix / "Ask user" / reply draft] |

If a comment thread has existing replies from others, note them in the plan.

**For items marked "Ask user":** present each one individually with the full comment and your proposed approach. Accept user's decision (fix/skip/reply) before moving to the next.

If `--dry-run`: show the unresolved comments table and proposed plan, then stop:

```
## Dry-Run Preview

PR: [PR_URL]
Branch: [BRANCH_NAME]
Unresolved comments: [N]
Proposed code fixes: [N]
Proposed replies: [N]
Blocked / ask-user items: [N]

No files changed. No commits created. No PR threads resolved.
```

**Checkpoint:** "Plan complete. Proceed with approved fixes? (yes / adjust / details [N] / skip-replies)"

- `yes` → apply all approved fixes in Step 4.
- `adjust` → re-plan with feedback.
- `details [N]` → show full comment body and proposed diff for item N before deciding.
- `skip-replies` → apply only code fixes, skip reply-only threads.

Track which thread IDs received code fixes (vs. replies). This mapping is needed in Step 6 to know which threads to resolve silently.

### Step 4: Apply Fixes (§3)

For each approved fix:

1. **Show the diff before committing.** Do not commit silently.
2. **Group commits** per these rules:
   - Multi-file fix → one commit for that fix
   - Single-file fixes → group up to 3 per commit
   - Bulk identical changes (e.g., typos, renames across many files) → one commit, unlimited files
   - For multi-fix commits, list each fix as a bullet in the commit body
3. **Commit message format**: `Fix PR comments [KEY]` (extract KEY from branch name: `([A-Z0-9]+-\d+)`, case-insensitive)
4. **Commit locally only.** Do not push until user says so.

### Step 5: Review Changes (§4)

After all fixes are committed, present the result in a review table.

**Code changes:**

| # | St | File | Author | Comment | Change |
|---|----|------|--------|---------|--------|
| 1 | 🔧 | `[path]:[line]` | @author | summary | `file.cs: old → new` |

If a single comment spans multiple files, list each file on its own line within the same row using compact inline diff (e.g., `file1.cs: old → new`, `file2.cs: deleted`). Do not create separate rows.

**Replies (no code change):**

| # | St | File | Author | Comment | Reply |
|---|----|------|--------|---------|-------|
| 2 | 💬 | `[path]:[line]` | @author | summary | drafted reply text |

**Checkpoint:** "Review the changes above. [N] code-fix threads will be resolved on push. Ready? (push / amend / further changes)"

- `push` → proceed to Step 6.
- `amend` → amend the last commit with requested changes, re-show this review table.
- `further changes` → make additional changes, re-show this review table.

### Step 6: Push and Resolve (§5)

Call `fix-pr` skill from `.ai/plugins/githubflow/fix-pr/SKILL.md` to push and resolve threads. Then call `jira-move` with `KEY` and milestone `code-review` (non-blocking).

Show summary:
```
✅ Round complete

Resolved this round: [N]
Replies pending user action: [N]
PR: [PR_URL]
```

### Step 7: Write Changelog and Update Progress

Skip if `--dry-run`.

**Write `TASK_DIR/changelog.md`:** Append a new iteration summarizing the fixes made this round. Use the same iteration-number-as-heading format:
- `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- `**Trigger:** PR review fixes`
- List each file changed and a brief description of the fix
- Create the file if it doesn't exist

**Update `TASK_DIR/plan.md` progress:**
- If exists: append progress row with status "Fixing", PR URL, timestamp, round number
- Else: create new file with status "Fixing"

### Step 8: Check for More Comments
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

Count threads where `isResolved` is `false`.

If any remain: "[N] new unresolved comments found. Continue fixing? (yes / no)"
- `yes` → loop back to **Step 2**. Skip Step 1 — branch and PR are already known.
- `no` → "Done for now. Run `dev-fix-pr` again when ready for the next round."

If zero remain: "✅ All comments resolved on this PR."
- Changelog: `TASK_DIR/changelog.md` updated
- Progress: `TASK_DIR/plan.md` updated
- Stop.

---

## Multi-Round Support

This skill supports multiple review rounds without re-invocation:

1. After each push, it checks for new unresolved comments.
2. If the reviewer added more comments, the skill loops back to Step 2 (listing) with a fresh fetch.
3. Each round produces its own commit(s) with the same `Fix PR comments [KEY]` message format.
4. The loop continues until all threads are resolved or the user chooses to stop.

---

## Rules Summary (from pr-rules.md)

| Rule | Detail |
|------|--------|
| Show diff before commit | Never commit silently |
| Commit message | `Fix PR comments [KEY]` |
| Commit grouping | Multi-file → 1 commit; single-file → max 3 per commit; bulk identical → unlimited |
| Push control | Never push without user approval |
| Resolve silently | Use GraphQL mutation, no reply on code-fix threads |
| Reply threads | Don't resolve via GraphQL; user handles in PR UI |
| Overlapping | Code change status supersedes reply status |
| Kept comments | If human already replied "keep it", skip — not unresolved |
