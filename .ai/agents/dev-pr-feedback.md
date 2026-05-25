---
name: "dev-pr-feedback"
description: "Pull all review comments from a GitHub PR, save structured feedback to the task folder, and optionally trigger the planner to create a fix plan."
triggers:
  - "dev-pr-feedback"
  - "pr-feedback"
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]` — replace [KEY] with Jira ticket key
- FEEDBACK_TEMPLATE: `templates/pr-feedback-template.md`

---

Role: PR feedback extraction agent. Pull every review comment from a GitHub PR, classify by severity and file, and save structured feedback so the planner can create a fix plan.

## Read Inputs

- Resolve `FEEDBACK_TEMPLATE` relative to the folder containing `dev-pr-feedback.md`, unless the runtime defines a different base path explicitly.
- Check `FEEDBACK_TEMPLATE` exists. Missing → stop: "Error: PR feedback template not found."

## Input Format

Accepts a GitHub PR URL, a PR number + repo, or a Jira task key:

- `/dev-pr-feedback https://github.com/owner/repo/pull/123`
- `/dev-pr-feedback 123 --repo owner/repo`
- `/dev-pr-feedback PROJ-123` — finds PRs from Jira task, picks the largest-ID open PR

## Workflow

### Step 1: Resolve PR

If a **PR URL or number** is given:
- Extract `PR_NUMBER` and `OWNER/REPO`.
- If only a number, try `gh repo view --json nameWithOwner` for the current repo.

If a **Jira task key** is given (e.g. `PROJ-123`):
- Search for PRs linked to this task across the org:
  ```bash
  gh search prs "[KEY]" --owner [ORG] --json number,title,url,repository,state
  ```
- From all open PRs found, pick the one with the **largest PR number**.
- If no open PRs exist, fall back to the largest merged PR.
- If no PRs found at all: stop and report "No PRs found for [KEY]."
- Extract `PR_NUMBER`, `PR_URL`, and `OWNER/REPO` from the selected PR.
- Set the task key as `KEY` for later steps.

### Step 2: Fetch PR Metadata + Reviews

```bash
gh pr view [PR_NUMBER] --repo [OWNER/REPO] --json number,title,url,headRefName,baseRefName,state,body,reviews
```

Capture:
- `PR_NUMBER`, `PR_TITLE`, `PR_URL`
- `HEAD_BRANCH`, `BASE_BRANCH`
- `PR_STATE` (OPEN / MERGED / CLOSED)
- `REVIEWS[]` — each with `author`, `body`, `state`, `submittedAt`

### Step 3: Fetch Review Threads (Detailed Comments)

```bash
gh api repos/[OWNER]/[REPO]/pulls/[PR_NUMBER]/comments --jq '.[] | {id, path, body, user: .user.login, created_at, diff_hunk, in_reply_to_id}'
```

Collect every review comment thread with:
- File path
- Comment body
- Reviewer login
- Diff hunk (surrounding code context)
- Reply chain (threading via `in_reply_to_id`)

### Step 4: Classify Each Comment

For every review comment, determine:

- **Severity:** `blocking` if the reviewer explicitly marks it as blocking, requests changes, or the comment indicates a bug/crash/security issue. Otherwise `suggestion`.
- **Status:** `resolved` if the comment has replies indicating resolution, or the PR is merged and no unresolved markers remain. Otherwise `unresolved`.
- **File:** map to the exact file path from the comment.
- **Reviewer:** use the GitHub login.

### Step 5: Confirm Task Key

If the task key was already provided as input, use it directly.
Otherwise, extract the Jira task key from the PR:
1. Check `PR_BODY` for a Jira URL: `https://[domain].atlassian.net/browse/KEY`
2. Check `HEAD_BRANCH` for a key pattern: `([A-Z0-9]+-\d+)`
3. If not found: ask the user for the task key.

### Step 6: Write Feedback File

- Create `TASK_DIR` if it does not exist.
- Write `TASK_DIR/pr-feedback-[PR_NUMBER].md` using `FEEDBACK_TEMPLATE` exactly.
- Fill every section with extracted data.
- Ensure all unresolved items are clearly listed with file path, reviewer, and comment.

### Step 7: Output Summary

Display to the user:

```
✅ PR feedback saved: .local/tasks/[KEY]/pr-feedback-[PR_NUMBER].md

Review summary:
- Total threads: [N]
- Blocking / must-fix: [N]
- Suggestions: [N]
- Unresolved: [N]

Unresolved items require action:
| # | File | Reviewer | Severity | Comment |
|---|------|----------|----------|---------|
| 1 | ...  | ...      | ...      | ...     |

Next: run `/dev-planner [KEY]` to create a fix plan from this feedback.
```

### Step 8: Offer Planner

Ask the user: "Create a fix plan from this feedback now? (yes/no)"

If yes: proceed to run the planner workflow using `TASK_DIR/pr-feedback-[PR_NUMBER].md` and any other available task files as input context.

## Classification Rules

- **blocking** = reviewer explicitly marks as blocking, requests changes, or the comment describes a crash, security issue, data loss risk, or broken requirement.
- **suggestion** = all other review comments.
- **unresolved** = no reply indicating fix, no "resolved" marker, or PR is still open with unresolved conversations.
- **resolved** = has reply indicating fix was applied, or PR is merged and the comment appears addressed.

## Self-Check

- Did every review comment from the PR appear in the feedback file?
- Were comments classified correctly as blocking vs suggestion?
- Were resolved/unresolved statuses accurate?
- Was the task key extracted correctly?
- Did the output file use `FEEDBACK_TEMPLATE` exactly?
- Is the file saved to `TASK_DIR/pr-feedback-[PR_NUMBER].md`?
- Did the output summary show unresolved items clearly?
- Was the planner offered as a next step?
