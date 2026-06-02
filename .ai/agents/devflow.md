---
name: "devflow"
description: "Smart development flow orchestrator. Detects task progress and suggests or runs the next skill automatically."
triggers:
  - "devflow"
  - "/devflow"
  - "/dev-flow"
role: Development flow orchestrator. Detect the current progress of a task, suggest the next action, and run the appropriate skill. Supports the full lifecycle: start → plan → code → review → ship → fix → finish → document.
---

## Paths

Read shared paths from `config.md`.

## Workflow

### Step 1: Resolve Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY. Stop if no valid KEY.

### Step 2: Setup Task Folder

If `TASK_DIR` does not exist, create it.
If `TASK_DIR/task.md` does not exist, prefer Jira MCP to fetch the issue. If MCP unavailable or fails, ask user for a short task summary and create `task.md` manually.

### Step 3: Detect Current Progress

Run checks in order. Check furthest progress first — first match wins. Each condition assumes all prior stages are complete (even if evidence files are missing — user may have joined mid-flow).

| # | Condition | Next Skill |
|---|-----------|------------|
| 1 | PR merged + ADR exists | All done |
| 2 | PR merged, no ADR | `8.dev-adr` |
| 3 | Open PR, `APPROVED` | `7.dev-finish` |
| 4 | Open PR, `CHANGES_REQUESTED` or `REVIEW_REQUIRED` | `1.dev-start` → `6.dev-fix-pr` |
| 5 | Open PR, awaiting review | "PR awaiting review. Check back later." |
| 6 | `TASK_DIR/review.md` exists | `5.dev-ship-pr-jira` |
| 7 | `TASK_DIR/changelog.md` exists | `4.dev-review` |
| 8 | `TASK_DIR/plan.md` exists | `3.dev-code` |
| 9 | Worktree exists for KEY | `2.dev-plan` |
| 10 | No worktree | `1.dev-start` |

**Detection commands:**

- Checks 1-2: `gh search prs [KEY] --merged --json number`
- Checks 3-5: `gh pr list --head [BRANCH] --state open --json reviewDecision`
- Checks 6-8: `test -f [TASK_DIR]/[file]`
- Check 9: `git worktree list | grep -i [KEY]`

**Guard:** If checks 6-7 match (review.md or changelog.md exists) but plan.md is missing, warn: "Task has code/review evidence but no plan.md. Run `/dev-plan [KEY]` first for a baseline before reviewing or shipping."

For checks 1-5, extract `BRANCH_NAME` from worktree (`git -C [WORKTREE_PATH] branch --show-current`) or legacy (`git branch --show-current`). If no branch, skip to check 6.

**For checks 3-5 (PR exists) — determine where to run the skill:**

| User state | Action |
|------------|--------|
| Already in worktree for KEY | Run suggested skill in the worktree. |
| On correct branch (legacy, no worktree) | Run suggested skill directly — `dev-fix-pr` supports legacy branch mode. |
| Neither worktree nor correct branch | Call `1.dev-start` first to create a worktree, then run the suggested skill inside it. |

**Chain example (check 4, no worktree, no branch):**
1. Run `1.dev-start/SKILL.md` with the KEY → creates worktree.
2. Tell user: `cd ../[REPO]-worktrees/[BRANCH]`.
3. Run `6.dev-fix-pr/SKILL.md` in the new worktree → lists and fixes PR comments.

### Step 4: Show Status and Suggest

Display what was found and the recommended next skill:

```
## Task Progress: [KEY]

| Stage | Status | Evidence |
|-------|--------|----------|
| Worktree | ✅ / ❌ | [path or "none"] |
| Plan | ✅ / ❌ | [TASK_DIR]/plan.md |
| Code | ✅ / ❌ | [TASK_DIR]/changelog.md |
| Review | ✅ / ❌ | [TASK_DIR]/review.md |
| PR | ✅ / ❌ | [PR_URL or "none"] |
| PR Status | [status] | — |

Next: /dev-[skill] [KEY]
```

If all stages are ✅ and PR is merged with ADR (or no ADR needed):
```
✅ Task [KEY] is complete. All stages done.
```

### Step 5: Run or Offer

Ask: "Run /dev-[skill] [KEY] now? (yes / no / manual)"

- `yes` → read and execute `[N].dev-[skill]/SKILL.md`.
- `no` → stop. User runs manually later.
- `manual` → stop. User handles this stage without the skill.

If the user provides a flag (`--plan-only`, `--code-only`, `--review-only`), skip detection and run that phase directly. These override the auto-detection for when the user wants to force a specific stage.

---

## Full Auto Mode

If user says `/devflow [KEY] --auto`: skip the "Run now?" prompt. Execute each skill in sequence automatically, stopping only at each skill's internal checkpoints. Continue through all stages until complete or the user stops at a checkpoint.

---

## Progress Tracking

After each skill completes, update the `## Progress` section in `TASK_DIR/plan.md` (skills handle this internally). The orchestrator reads the progress checkboxes and table to determine current state.
